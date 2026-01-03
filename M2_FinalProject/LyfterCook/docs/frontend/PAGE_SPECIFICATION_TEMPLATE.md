# Page Specification Template

> Use this template for each page you want to build. Copy this file, rename it (e.g., `CLIENTS_PAGE_SPEC.md`), and fill in all sections.

---

## Page Name: [e.g., Clients Management]

**File Path**: `pages/dashboard/clients.html`  
**URL**: `/pages/dashboard/clients.html`  
**Access**: Protected (requires authentication, role: chef)

---

## 1. Purpose
What does this page do? What problem does it solve?

**Example**:  
_"This page allows chefs to manage their client database. They can add new clients, view existing clients, edit client details, and delete clients. It helps chefs keep track of dietary restrictions, contact information, and event history."_

---

## 2. User Stories
Who uses this page and what do they want to accomplish?

**Example**:
- As a chef, I want to see all my clients in one place so I can quickly find their contact information.
- As a chef, I want to add a new client with their dietary restrictions so I can remember them for future events.
- As a chef, I want to search for a client by name so I don't have to scroll through a long list.

---

## 3. Layout Description
Describe the visual structure of the page. You can use text or ASCII art.

**Example**:
```
+------------------------------------------------------------+
|  [Logo]                     Clients                  [User]|
+------------------------------------------------------------+
|                                                            |
|  [Search Bar]              [+ Add Client Button]          |
|                                                            |
|  +------------------------------------------------------+  |
|  | Name         | Email          | Phone    | Actions  |  |
|  +------------------------------------------------------+  |
|  | John Doe     | john@email.com | 555-1234 | Edit Del |  |
|  | Jane Smith   | jane@email.com | 555-5678 | Edit Del |  |
|  | ...          | ...            | ...      | ...      |  |
|  +------------------------------------------------------+  |
|                                                            |
|  [< Previous]  [1] [2] [3] [4] [5]  [Next >]              |
|                                                            |
+------------------------------------------------------------+
```

**Alternative**: Provide a link to a wireframe image or Figma/Excalidraw link.

---

## 4. Components
List all UI elements and interactions.

### 4.1 Header
- Navigation bar with logo, page title, and user menu

### 4.2 Search Bar
- **Type**: Text input
- **Placeholder**: "Search by name or email..."
- **Behavior**: Filters table in real-time (debounced)

### 4.3 Add Client Button
- **Label**: "+ Add Client"
- **Action**: Opens modal with client form

### 4.4 Client Table
- **Columns**:
  - Name (sortable)
  - Email (sortable)
  - Phone
  - Dietary Restrictions (truncated if long)
  - Actions (Edit, Delete)
- **Rows**: 20 clients per page
- **Empty State**: "No clients found. Add your first client!"

### 4.5 Edit Button (per row)
- **Icon**: Pencil icon
- **Action**: Opens modal with pre-filled client form

### 4.6 Delete Button (per row)
- **Icon**: Trash icon
- **Action**: Shows confirmation dialog → deletes client on confirm

### 4.7 Pagination
- **Controls**: Previous, page numbers (1-5), Next
- **Behavior**: Loads new page of clients on click

---

## 5. Forms & Inputs
Detail any forms on the page.

### Add/Edit Client Form (Modal)

**Fields**:
1. **Full Name** (required)
   - Type: Text input
   - Validation: Min 2 characters, max 100
   - Error: "Name must be at least 2 characters"

2. **Email** (required)
   - Type: Email input
   - Validation: Valid email format
   - Error: "Please enter a valid email"

3. **Phone** (optional)
   - Type: Tel input
   - Format: (555) 555-5555
   - Validation: 10 digits

4. **Dietary Restrictions** (optional)
   - Type: Textarea
   - Max length: 500 characters
   - Placeholder: "e.g., Gluten-free, Vegetarian, Nut allergy"

5. **Notes** (optional)
   - Type: Textarea
   - Max length: 1000 characters

**Buttons**:
- **Save**: Submit form (POST or PUT)
- **Cancel**: Close modal without saving

**Validation**:
- Show error messages below each field
- Disable "Save" button if required fields are empty

---

## 6. API Endpoints
List all API calls this page makes.

| Method | Endpoint | Purpose | Request Body | Response |
|--------|----------|---------|--------------|----------|
| GET | `/clients?page=1&per_page=20&search=john` | Fetch clients | None | `{data: [...], total: 50}` |
| POST | `/clients` | Create client | `{name, email, phone, dietary_restrictions}` | `{data: {...}}` |
| PUT | `/clients/:id` | Update client | `{name, email, phone, dietary_restrictions}` | `{data: {...}}` |
| DELETE | `/clients/:id` | Delete client | None | `{message: "Client deleted"}` |

---

## 7. User Interactions
Describe what happens when the user performs actions.

### Scenario 1: Add New Client
1. User clicks "+ Add Client" button
2. Modal opens with empty form
3. User fills in name and email (required), leaves phone blank
4. User clicks "Save"
5. Frontend validates: name (✓), email (✓)
6. Frontend calls `POST /clients`
7. Backend responds with success → modal closes, table refreshes, shows toast "Client added successfully!"

### Scenario 2: Search for Client
1. User types "john" in search bar
2. After 500ms (debounce), frontend calls `GET /clients?search=john`
3. Table updates to show only clients with "john" in name or email
4. If no results, show empty state message

### Scenario 3: Delete Client
1. User clicks trash icon on "John Doe" row
2. Confirmation dialog appears: "Are you sure you want to delete John Doe?"
3. User clicks "Confirm"
4. Frontend calls `DELETE /clients/123`
5. Backend responds with success → row disappears from table, shows toast "Client deleted"

---

## 8. Error Handling
What happens when things go wrong?

| Error | Cause | User Experience |
|-------|-------|-----------------|
| 400 Bad Request | Invalid email format | Show error message below email field: "Email is already in use" |
| 401 Unauthorized | JWT token expired | Redirect to login page with message: "Session expired. Please log in again." |
| 404 Not Found | Client doesn't exist | Show toast: "Client not found. It may have been deleted." |
| 500 Server Error | Backend crash | Show toast: "Something went wrong. Please try again." |
| Network Error | No internet | Show toast: "Network error. Check your connection." |

---

## 9. Loading States
How does the page indicate work in progress?

- **Initial Load**: Show skeleton table with 5 placeholder rows
- **Pagination**: Disable pagination buttons, show spinner in table
- **Form Submit**: Disable "Save" button, show spinner inside button, change text to "Saving..."
- **Delete**: Disable row actions, show spinner in row

---

## 10. Success States
What feedback does the user get when actions succeed?

- **Client Added**: Green toast notification "Client added successfully!" (auto-dismiss after 3 seconds)
- **Client Updated**: Green toast "Client updated!"
- **Client Deleted**: Green toast "Client deleted!"

---

## 11. Responsive Design
How does the page adapt to different screen sizes?

| Screen Size | Layout Changes |
|-------------|----------------|
| Desktop (>1024px) | Full table with all columns, sidebar visible |
| Tablet (768-1024px) | Hide "Dietary Restrictions" column, collapse sidebar |
| Mobile (<768px) | Switch to card layout (no table), stack cards vertically |

**Mobile Card Example**:
```
+---------------------+
| John Doe            |
| john@email.com      |
| (555) 555-1234      |
| [Edit] [Delete]     |
+---------------------+
```

---

## 12. Accessibility
How do we make this page usable for everyone?

- **Keyboard Navigation**: 
  - Tab through search bar → Add button → table rows → pagination
  - Enter on row opens edit modal
  - Escape closes modals
- **Screen Readers**: 
  - Add `aria-label` to buttons ("Edit John Doe", "Delete John Doe")
  - Announce table updates ("Showing 10 of 50 clients")
- **Focus States**: Visible focus outline on all interactive elements
- **Color Contrast**: Minimum 4.5:1 ratio for text

---

## 13. Design References
Links to design inspiration or similar pages.

- [Airtable Grid View](https://www.airtable.com) - Table layout inspiration
- [Notion Database](https://www.notion.so) - Modal form inspiration
- [Stripe Dashboard](https://dashboard.stripe.com/customers) - Overall aesthetic

---

## 14. Open Questions
What do you still need to decide?

- Should we allow bulk delete (select multiple clients)?
- Do we need to export clients to CSV?
- Should phone numbers be automatically formatted as user types?
- Do we want to track "last contacted" date for each client?

---

## 15. Out of Scope (For Now)
Features to consider in future iterations.

- Client tagging/categorization
- Event history per client
- Import clients from CSV
- Send email to client directly from this page
- Client profile page with detailed event history

---

## Status Tracking

- [ ] Wireframe created
- [ ] Design approved
- [ ] HTML structure complete
- [ ] CSS styling complete
- [ ] JavaScript logic complete
- [ ] API integration complete
- [ ] Testing complete
- [ ] Deployed to production

---

**Last Updated**: [Date]  
**Owner**: [Your Name]
