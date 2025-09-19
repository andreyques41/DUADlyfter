from flask import Flask
from exercise3.user_routes import UserAPI
from exercise3.car_routes import CarAPI
from exercise3.rental_routes import RentalAPI
from utilities.db import PgManager


def create_app():
    app = Flask(__name__)

    # Initialize database manager
    db_manager = PgManager(
        db_name="postgres", user="postgres", password="postgres", host="localhost"
    )

    # Initialize User API with database manager
    user_view = UserAPI.as_view("user_api", db_manager=db_manager)
    app.add_url_rule(
        "/users/",
        defaults={"user_id": None},
        view_func=user_view,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/users/<int:user_id>", view_func=user_view, methods=["GET", "PUT", "DELETE"]
    )

    # Initialize Car API with database manager
    car_view = CarAPI.as_view("car_api", db_manager=db_manager)
    app.add_url_rule(
        "/cars/", defaults={"car_id": None}, view_func=car_view, methods=["GET", "POST"]
    )
    app.add_url_rule(
        "/cars/<int:car_id>", view_func=car_view, methods=["GET", "PUT", "DELETE"]
    )

    # Initialize Rental API with database manager
    rental_view = RentalAPI.as_view("rental_api", db_manager=db_manager)
    app.add_url_rule(
        "/rentals/",
        defaults={"rental_id": None},
        view_func=rental_view,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/rentals/<int:rental_id>",
        view_func=rental_view,
        methods=["GET", "PUT", "DELETE"],
    )

    return app


def run_api():
    app = create_app()
    app.run(host="localhost", debug=True, port=8000, use_reloader=False)


if __name__ == "__main__":
    run_api()
