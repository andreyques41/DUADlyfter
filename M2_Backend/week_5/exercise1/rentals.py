from utilities.db import PgManager


def create_rentals(db_manager: PgManager):
    db_manager.execute_query(
        """
        CREATE TABLE lyfter_car_rental.rent_state (
            id SERIAL PRIMARY KEY,
            state VARCHAR(20) UNIQUE
        );
        """
    )

    db_manager.execute_query(
        """
        CREATE TABLE lyfter_car_rental.rentals(
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES lyfter_car_rental.users(id) ON UPDATE CASCADE ON DELETE CASCADE,
            car_id INT REFERENCES lyfter_car_rental.cars(id) ON UPDATE CASCADE ON DELETE CASCADE,
            created_date DATE DEFAULT CURRENT_DATE,
            state_id INT REFERENCES lyfter_car_rental.rent_state(id) ON UPDATE CASCADE ON DELETE RESTRICT
        );
        """
    )

    db_manager.execute_query(
        """
        INSERT INTO lyfter_car_rental.rent_state (state) VALUES
        ('activo'),
        ('completado'),
        ('cancelado');
        """
    )

    db_manager.execute_query(
        """
        INSERT INTO lyfter_car_rental.rentals (user_id, car_id, created_date, state_id) VALUES
        (1, 3, '2025-09-01', 2),
        (5, 1, '2025-08-15', 1),
        (12, 8, '2025-07-22', 2),
        (23, 4, '2025-09-10', 1),
        (34, 6, '2025-06-30', 2),
        (45, 9, '2025-09-05', 3),
        (18, 2, '2025-08-28', 1),
        (29, 7, '2025-07-18', 2),
        (7, 10, '2025-09-03', 2),
        (41, 5, '2025-08-25', 1);
        """
    )
