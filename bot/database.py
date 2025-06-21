from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from bot.config import DATABASE_URL

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    is_subscribed = Column(Boolean, default=False)
    subscription_expires = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    alerts = relationship("Alert", back_populates="user")

class Alert(Base):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    coin = Column(String, nullable=False)
    condition = Column(String, nullable=False)  # '>', '<', '='
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="alerts")

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'macro', 'altcoin', 'whale', 'onchain'
    posted_at = Column(DateTime, default=datetime.utcnow)
    channel_message_id = Column(Integer)

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

Session = init_db() 