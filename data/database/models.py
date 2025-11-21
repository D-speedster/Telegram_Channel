from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
import datetime

# Import database path from config
from src.config import DATABASE_PATH

# --- SQLAlchemy Setup ---
engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Database Models ---

class Admin(Base):
    """Admin users table."""
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<Admin(user_id={self.user_id}, username='{self.username}')>"

class PostType(Base):
    """Post types table (e.g., 'text', 'photo', 'video')."""
    __tablename__ = 'post_types'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    # Relationship to PostLog
    logs = relationship("PostLog", back_populates="post_type")

    def __repr__(self):
        return f"<PostType(name='{self.name}')>"

class PostLog(Base):
    """Log of all posts sent by the bot."""
    __tablename__ = 'posts_log'
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, nullable=False)
    post_type_id = Column(Integer, ForeignKey('post_types.id'), nullable=False)
    content = Column(Text, nullable=True) # For text messages or captions
    file_id = Column(String(255), nullable=True) # For photos, videos, etc.
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to PostType
    post_type = relationship("PostType", back_populates="logs")

    def __repr__(self):
        return f"<PostLog(id={self.id}, sender_id={self.sender_id}, type='{self.post_type.name}')>"

# --- Utility Function to get a DB session ---
def get_db():
    """Dependency to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()