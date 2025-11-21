from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func
from src.config import DATABASE_PATH

Base = declarative_base()

class PostType(Base):
    __tablename__ = 'post_types'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False, index=True)
    banner_file = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<PostType(id={self.id}, name='{self.name}')>"

class PostLog(Base):
    __tablename__ = 'post_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_type_id = Column(Integer, ForeignKey('post_types.id', ondelete='CASCADE'))
    post_type = relationship("PostType", backref="logs")
    text = Column(String, nullable=False)
    media_path = Column(String, nullable=True)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_by = Column(Integer, nullable=False) # Admin User ID
    
    def __repr__(self):
        return f"<PostLog(id={self.id}, post_type_id={self.post_type_id}, sent_by={self.sent_by})>"

# Create engine with better configuration
engine = create_engine(
    f'sqlite:///{DATABASE_PATH}',
    echo=False,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Generator function for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()