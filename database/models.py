from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """Модель пользователя."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    language_code = Column(String)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    settings = Column(JSON, default={})
    
    alerts = relationship("Alert", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    
class Alert(Base):
    """Модель уведомления."""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)  # price, volume, whale
    symbol = Column(String)
    network = Column(String, nullable=True)
    value = Column(Float)
    condition = Column(String)  # above, below
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="alerts")
    
class Notification(Base):
    """Модель отправленного уведомления."""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)
    title = Column(String)
    message = Column(String)
    data = Column(JSON, default={})
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="notifications")
    
class MarketData(Base):
    """Модель рыночных данных."""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    price = Column(Float)
    volume_24h = Column(Float)
    change_24h = Column(Float)
    high_24h = Column(Float)
    low_24h = Column(Float)
    market_cap = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
class WhaleTransaction(Base):
    """Модель транзакции кита."""
    __tablename__ = "whale_transactions"
    
    id = Column(Integer, primary_key=True)
    network = Column(String)
    tx_hash = Column(String, unique=True)
    from_address = Column(String)
    to_address = Column(String)
    amount = Column(Float)
    amount_usd = Column(Float)
    token = Column(String)
    timestamp = Column(DateTime)
    block_number = Column(Integer)
    
class TechnicalSignal(Base):
    """Модель технического сигнала."""
    __tablename__ = "technical_signals"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    timeframe = Column(String)
    signal_type = Column(String)  # buy, sell, neutral
    strength = Column(String)  # weak, medium, strong
    indicators = Column(JSON)
    patterns = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class EconomicEvent(Base):
    """Модель экономического события."""
    __tablename__ = "economic_events"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    date = Column(DateTime)
    country = Column(String)
    impact = Column(String)  # low, medium, high
    forecast = Column(String)
    previous = Column(String)
    actual = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class NewsItem(Base):
    """Модель новости."""
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    summary = Column(String)
    source = Column(String)
    url = Column(String)
    impact = Column(String)  # positive, negative, neutral
    categories = Column(JSON)
    currencies = Column(JSON)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class UserActivity(Base):
    """Модель активности пользователя."""
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    
class ErrorLog(Base):
    """Модель лога ошибок."""
    __tablename__ = "error_logs"
    
    id = Column(Integer, primary_key=True)
    error_type = Column(String)
    error_message = Column(String)
    traceback = Column(String)
    user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow) 