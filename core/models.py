from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class Sector(Base):
    __tablename__ = "sectors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    
    # Relationships
    stocks = relationship("Stock", back_populates="sector")

class Stock(Base):
    __tablename__ = "stocks"
    
    symbol = Column(String, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"))
    
    # Pricing
    close_price = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    
    # Audit
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    sector = relationship("Sector", back_populates="stocks")

class MFCategory(Base):
    __tablename__ = "mf_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    
    # Relationships
    mutual_funds = relationship("MutualFund", back_populates="category")

class MutualFund(Base):
    __tablename__ = "mutual_funds"
    
    search_id = Column(String, primary_key=True, index=True)
    scheme_name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("mf_categories.id"))
    
    # Metrics
    return_3y = Column(Float, nullable=True)
    return_5y = Column(Float, nullable=True)
    fund_manager = Column(String, nullable=True)
    
    # Audit
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    category = relationship("MFCategory", back_populates="mutual_funds")
