from cache_manager import CacheManager
from flask import Flask, request, jsonify
import os
user_repository = None
app = Flask(__name__)

cache_manager = CacheManager(
    host=os.environ.get("REDIS_HOST"),
    port=int(os.environ.get("REDIS_PORT")),
    password=os.environ.get("REDIS_PASSWORD"),
)

cache_manager.store_data("full_name", "John Doe")
cache_manager.store_data("important_key", "Important Value!", time_to_live=100)


def generate_cache_users_page_key(page):
    return f'getUsers-page{page}'
    

@app.route('/users/{page}/', methods=['GET'])
def get_users(page):
		page_key = generate_cache_users_page_key(page)
		if cache_manager.check_key(page_key):
			return cache_manager.get_data(page_key)
		else:
			results = user_repository.get_all()
			# Toda la lógica para cachear las pages

@app.route('/update_user/{_id}', methods=['POST'])
def update_user(_id):
    # Toda la lógica para actualizar el usuario

		# Eliminacion de las paginas cacheadas
    cache_manager.delete_data_with_pattern("getUsers-page")

    return jsonify({'status': 'user updated'})