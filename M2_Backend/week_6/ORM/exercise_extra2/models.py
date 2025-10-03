from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# This is the standard way: define ORM classes with explicit columns
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'backend_week6'}
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    username = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=True)
    birthday = Column(Date, nullable=True)
    
    # Define relationships to other tables
    cars = relationship("Car", back_populates="user")
    addresses = relationship("Address", back_populates="user")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Brand(Base):
    __tablename__ = 'brands'
    __table_args__ = {'schema': 'backend_week6'}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    country_origin = Column(String(50), nullable=True)
    
    cars = relationship("Car", back_populates="brand")
    
    def __repr__(self):
        return f"<Brand(name='{self.name}')>"

class Car(Base):
    __tablename__ = 'cars'
    __table_args__ = {'schema': 'backend_week6'}
    
    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey('backend_week6.brands.id'), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=True)
    color = Column(String(30), nullable=True)
    license_plate = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey('backend_week6.users.id'), nullable=True)
    
    brand = relationship("Brand", back_populates="cars")
    user = relationship("User", back_populates="cars")
    
    def __repr__(self):
        return f"<Car(model='{self.model}', year={self.year})>"

class Location(Base):
    __tablename__ = 'locations'
    __table_args__ = {'schema': 'backend_week6'}
    
    id = Column(Integer, primary_key=True)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=True)
    country = Column(String(50), nullable=False)
    
    addresses = relationship("Address", back_populates="location")
    
    def __repr__(self):
        return f"<Location(city='{self.city}', country='{self.country}')>"

class Address(Base):
    __tablename__ = 'addresses'
    __table_args__ = {'schema': 'backend_week6'}
    
    id = Column(Integer, primary_key=True)
    street = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=True)
    location_id = Column(Integer, ForeignKey('backend_week6.locations.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('backend_week6.users.id'), nullable=False)
    
    location = relationship("Location", back_populates="addresses")
    user = relationship("User", back_populates="addresses")
    
    def __repr__(self):
        return f"<Address(street='{self.street}')>"