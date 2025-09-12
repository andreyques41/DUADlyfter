-- Normalize rent state
CREATE TABLE lyfter_car_rental.rent_state (
	id SERIAL PRIMARY KEY,
	state VARCHAR(20) UNIQUE
);

CREATE TABLE lyfter_car_rental.rentals(
	id SERIAL PRIMARY KEY,
    user_id INT REFERENCES lyfter_car_rental.users(id) ON UPDATE CASCADE ON DELETE CASCADE,
    car_id INT REFERENCES lyfter_car_rental.cars(id) ON UPDATE CASCADE ON DELETE CASCADE,
    created_date DATE DEFAULT CURRENT_DATE,
	state_id INT REFERENCES lyfter_car_rental.rent_state(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Insert rental states
INSERT INTO lyfter_car_rental.rent_state (state) VALUES
('activo'),
('completado'),
('cancelado');

-- Insert sample rentals (cross table between users and cars)
-- State IDs: 1 = activo, 2 = completado, 3 = cancelado
INSERT INTO lyfter_car_rental.rentals (user_id, car_id, state_id) VALUES
(1, 3, 2),
(5, 1, 1),
(12, 8, 2),
(23, 4, 1),
(34, 6, 2),
(45, 9, 3),
(18, 2, 1),
(29, 7, 2),
(7, 10, 2),
(41, 5, 1);