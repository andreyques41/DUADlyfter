from sqlalchemy import create_engine
from exercise_extra2.user_orm_repository import UserOrmRepository

def orm_queries():
    """Demo: ORM relationships and related data access."""
    DB_URI = 'postgresql://postgres:postgres@localhost:5432/lyfter'
    engine = create_engine(DB_URI, echo=False)
    user_repo = UserOrmRepository(engine)
    user_repo.get_user_with_relationships(1)
    
if __name__ == "__main__":
    orm_queries()