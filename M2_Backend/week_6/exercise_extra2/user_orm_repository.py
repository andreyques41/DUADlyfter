from sqlalchemy.orm import sessionmaker
from exercise_extra2.models import User, Car, Address, Brand, Location

class UserOrmRepository:
    def _get_or_create_brand(self, session, name, country):
        """Get or create a brand by name and country."""
        brand = session.query(Brand).filter_by(name=name).first()
        if not brand:
            brand = Brand(name=name, country_origin=country)
            session.add(brand)
            session.flush()
        return brand

    def _get_or_create_location(self, session, city, state, country):
        """Get or create a location by city, state, and country."""
        location = session.query(Location).filter_by(city=city, state=state, country=country).first()
        if not location:
            location = Location(city=city, state=state, country=country)
            session.add(location)
            session.flush()
        return location

    def __init__(self, engine):
        """Initialize repository with engine."""
        self.Session = sessionmaker(bind=engine)

    def get_user_with_relationships(self, user_id):
        """Return user with related cars and addresses."""
        session = self.Session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                print(f"User: {user.username} ({user.email})")
                print(f"Cars: {len(user.cars)}")
                for car in user.cars:
                    print(f"  - {car.brand.name} {car.model} ({car.year}) - {car.color}")
                print(f"Addresses: {len(user.addresses)}")
                for address in user.addresses:
                    print(f"  - {address.street}, {address.location.city}, {address.location.country}")
                return user
            else:
                print(f"No user found with ID {user_id}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            session.close()

    def insert_new_user(self, full_name, username, email, phone, birthday,
                        street, postal_code, city, state, country,
                        car_model, car_year, car_color, car_license_plate, brand_name, brand_country):
        """Insert a new user with address and car. Returns the user object."""
        session = self.Session()
        try:
            brand = self._get_or_create_brand(session, brand_name, brand_country)
            location = self._get_or_create_location(session, city, state, country)

            user = User(
                full_name=full_name,
                username=username,
                email=email,
                phone=phone,
                birthday=birthday
            )

            address = Address(
                street=street,
                postal_code=postal_code,
                location=location,
                user=user
            )

            car = Car(
                brand=brand,
                model=car_model,
                year=car_year,
                color=car_color,
                license_plate=car_license_plate,
                user=user
            )

            session.add_all([user, address, car])
            session.commit()
            print(f"Inserted user {user.username} with address and car.")
            return user
        except Exception as e:
            session.rollback()
            print(f"Error inserting user: {e}")
            return None
        finally:
            session.close()