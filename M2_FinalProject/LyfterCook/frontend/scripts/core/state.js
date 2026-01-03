// frontend/scripts/core/state.js
import api from '../services/api.js';

const TOKEN_STORAGE_KEY = 'token';

function defaultLoginRedirect() {
  // Use absolute path so it works from any dashboard route.
  window.location.href = '/pages/auth/login.html';
}

class AppState {
  constructor() {
    this._listeners = new Set();
    this._initialized = false;

    this.token = null;
    this.user = null;
    this.status = 'anonymous'; // 'anonymous' | 'loading' | 'authenticated'
  }

  subscribe(listener) {
    this._listeners.add(listener);
    return () => this._listeners.delete(listener);
  }

  _emit() {
    for (const listener of this._listeners) {
      try {
        listener(this);
      } catch (err) {
        // Avoid breaking app flow if a subscriber throws.
        console.error('AppState subscriber error:', err);
      }
    }
  }

  isAuthenticated() {
    return Boolean(this.token);
  }

  getToken() {
    return this.token;
  }

  setToken(token) {
    this.token = token || null;
    if (this.token) {
      localStorage.setItem(TOKEN_STORAGE_KEY, this.token);
    } else {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
    }
    this._emit();
  }

  setUser(user) {
    this.user = user || null;
    this.status = this.user ? 'authenticated' : this.token ? 'loading' : 'anonymous';
    this._emit();
  }

  async refreshMe() {
    if (!this.token) {
      this.setUser(null);
      return null;
    }

    this.status = 'loading';
    this._emit();

    try {
      const response = await api.get('/auth/me');
      const user = response?.data?.data ?? null;
      this.setUser(user);
      return user;
    } catch (err) {
      // If the token is invalid/expired, api interceptor will clear token + redirect.
      // Still reflect anonymous state if we're still on-page.
      this.setUser(null);
      throw err;
    }
  }

  async init() {
    if (this._initialized) return;
    this._initialized = true;

    const token = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (!token) {
      this.setToken(null);
      this.setUser(null);
      return;
    }

    this.setToken(token);
    await this.refreshMe();
  }

  logout({ redirect = true } = {}) {
    this.setToken(null);
    this.setUser(null);

    if (redirect) {
      defaultLoginRedirect();
    }
  }

  redirectToLogin() {
    defaultLoginRedirect();
  }
}

export const appState = new AppState();
