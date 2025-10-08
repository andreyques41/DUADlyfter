
import random
from faker import Faker
from exercise_extra2.user_orm_repository import UserOrmRepository
from sqlalchemy import create_engine

CAR_MODELS = ["Civic", "Corolla", "Focus", "Model 3", "Sentra", "Jetta", "Mazda3", "Elantra"]
CAR_COLORS = ["Red", "Blue", "Black", "White", "Silver", "Green", "Yellow"]
BRANDS = [
    ("Toyota", "Japan"),
    ("Honda", "Japan"),
    ("Ford", "USA"),
    ("Volkswagen", "Germany"),
    ("Mazda", "Japan"),
    ("Nissan", "Japan"),
    ("Hyundai", "South Korea")
]

def generate_users(engine, fake, count=20):
    print(f"[INFO] Generating {count} fake users...")
    user_repo = UserOrmRepository(engine)
    for i in range(count):
        try:
            brand_name, brand_country = random.choice(BRANDS)
            user_repo.insert_new_user(
                full_name=fake.name()[:100],
                username=fake.user_name()[:50],
                email=fake.email()[:100],
                phone=fake.phone_number()[:20],
                birthday=fake.date_of_birth(minimum_age=18, maximum_age=80),
                street=fake.street_address()[:100],
                postal_code=fake.postcode()[:20],
                city=fake.city()[:100],
                state=fake.state()[:50],
                country=fake.country()[:50],
                car_model=random.choice(CAR_MODELS)[:50],
                car_year=random.randint(2000, 2023),
                car_color=random.choice(CAR_COLORS)[:30],
                car_license_plate=fake.license_plate()[:20],
                brand_name=brand_name[:50],
                brand_country=brand_country[:50]
            )
        except Exception as e:
            print(f"[WARN] Skipped user due to error: {e}")

def run_seeding():
    DB_URI = 'postgresql://postgres:postgres@localhost:5432/lyfter'
    engine = create_engine(DB_URI, echo=False)
    fake = Faker()
    generate_users(engine, fake, 20)
    return True
