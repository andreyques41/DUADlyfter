CREATE TABLE lyfter_car_rental.model (
	id SERIAL PRIMARY KEY,
	brand VARCHAR(20),
	name VARCHAR(20)
);

-- Normalize car state
CREATE TABLE lyfter_car_rental.car_state (
	id SERIAL PRIMARY KEY,
	state VARCHAR(20) UNIQUE
);

CREATE TABLE lyfter_car_rental.cars(
	id SERIAL PRIMARY KEY,
	model_id INT REFERENCES lyfter_car_rental.model(id) ON UPDATE CASCADE ON DELETE RESTRICT,
	year INT,
	state_id INT REFERENCES lyfter_car_rental.car_state(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Insert random models
INSERT INTO lyfter_car_rental.model (brand, name) VALUES
('Toyota', 'Corolla'),
('Honda', 'Civic'),
('Ford', 'Focus'),
('Chevrolet', 'Malibu'),
('Nissan', 'Sentra');

-- Insert car states
INSERT INTO lyfter_car_rental.car_state (state) VALUES
('disponible'),
('en_mantenimiento'),
('alquilado');

-- Insert 10 random cars referencing the above models (model_id 1-5)
-- State IDs: 1 = disponible, 2 = en_mantenimiento, 3 = alquilado
INSERT INTO lyfter_car_rental.cars (model_id, year, state_id) VALUES
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