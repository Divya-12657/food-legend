from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db_setup import Base
import uuid


# Donor model
class Donor(Base):
    __tablename__ = 'donors'
    __table_args__ = {'schema': 'food_app'}

    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey('food_app.users.id'), nullable=False)
    food_type = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    location = Column(String, nullable=False, index=True)
    status = Column(String, default="available", nullable=False)
    receiver_id = Column(Integer, ForeignKey('food_app.users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="donations", foreign_keys=[user_id])
    receiver = relationship("User", back_populates="received_donations", foreign_keys=[receiver_id])


# User model
class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema':'food_app'}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="donor")  # "donor", "receiver", or other roles
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    donations = relationship("Donor", back_populates="user", foreign_keys=[Donor.user_id])
    received_donations = relationship("Donor", back_populates="receiver", foreign_keys=[Donor.receiver_id])
