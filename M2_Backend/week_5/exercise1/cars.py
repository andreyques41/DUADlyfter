from utilities.db import PgManager


def create_cars(db_manager: PgManager):
    db_manager.execute_query(
        """
        CREATE TABLE model (
            id SERIAL PRIMARY KEY,
            brand VARCHAR(20),
            name VARCHAR(20)
        );
        """
    )

    db_manager.execute_query(
        """
        CREATE TABLE car_state (
            id SERIAL PRIMARY KEY,
            state VARCHAR(20) UNIQUE
        );
        """
    )

    db_manager.execute_query(
        """
        CREATE TABLE cars(
            id SERIAL PRIMARY KEY,
            model_id INT REFERENCES model(id) ON UPDATE CASCADE ON DELETE RESTRICT,
            year INT,
            state_id INT REFERENCES car_state(id) ON UPDATE CASCADE ON DELETE RESTRICT
        );
        """
    )

    db_manager.execute_query(
        """
        INSERT INTO model (brand, name) VALUES
        ('Toyota', 'Corolla'),
        ('Honda', 'Civic'),
        ('Ford', 'Focus'),
        ('Chevrolet', 'Malibu'),
        ('Nissan', 'Sentra');
        """
    )

    db_manager.execute_query(
        """
        INSERT INTO car_state (state) VALUES
        ('disponible'),
        ('en_mantenimiento'),
        ('alquilado');
        """
    )
    db_manager.execute_query(
        """
        INSERT INTO cars (model_id, year, state_id) VALUES
        (1, 2017, 1),
        (2, 2019, 2),
        (3, 2018, 3),
        (4, 2020, 1),
        (5, 2016, 3),
        (2, 2021, 1),
        (3, 2015, 2),
        (1, 2018, 3),
        (5, 2019, 1),
        (5, 2017, 2);
        """
    )
