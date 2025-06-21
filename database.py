from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from config import DATABASE_URL

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_premium = Column(Boolean, default=False)
    subscription_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    alerts = relationship("PriceAlert", back_populates="user", cascade="all, delete-orphan")

class PriceAlert(Base):
    __tablename__ = 'price_alerts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    symbol = Column(String, nullable=False)
    condition = Column(String, nullable=False)  # 'above' или 'below'
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime)
    
    user = relationship("User", back_populates="alerts")

def init_db(database_url: str = 'sqlite:///db/quantnews.db') -> None:
    """Инициализация базы данных."""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

def get_session(database_url: str = 'sqlite:///db/quantnews.db') -> sessionmaker:
    """Получение сессии базы данных."""
    engine = create_engine(database_url)
    return sessionmaker(bind=engine)() 