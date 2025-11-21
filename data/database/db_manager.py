from sqlalchemy.orm import Session
from .models import Admin, PostType, PostLog, SessionLocal, Base, engine
import datetime

class DBManager:
    """Manages all database operations."""

    def __init__(self):
        """Initializes the DBManager."""
        self.db_session = SessionLocal()

    def create_tables(self):
        """Creates all tables in the database based on the models."""
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")

    def get_admins(self) -> list[Admin]:
        """Returns a list of all admin users."""
        return self.db_session.query(Admin).all()

    def get_post_types(self) -> list[PostType]:
        """Returns a list of all available post types."""
        return self.db_session.query(PostType).all()

    def add_post_log(self, sender_id: int, post_type_name: str, content: str = None, file_id: str = None):
        """Adds a new record to the posts_log table."""
        post_type = self.db_session.query(PostType).filter_by(name=post_type_name).first()
        if not post_type:
            raise ValueError(f"Post type '{post_type_name}' not found.")

        new_log = PostLog(
            sender_id=sender_id,
            post_type_id=post_type.id,
            content=content,
            file_id=file_id,
            sent_at=datetime.datetime.utcnow()
        )
        self.db_session.add(new_log)
        self.db_session.commit()
        print(f"New post log added: User {sender_id}, Type {post_type_name}")

    def add_post_type(self, name: str) -> PostType:
        """Adds a new post type if it doesn't already exist."""
        existing_type = self.db_session.query(PostType).filter_by(name=name).first()
        if existing_type:
            print(f"Post type '{name}' already exists.")
            return existing_type

        new_type = PostType(name=name)
        self.db_session.add(new_type)
        self.db_session.commit()
        print(f"Post type '{name}' added successfully.")
        return new_type

    def close_session(self):
        """Closes the database session."""
        self.db_session.close()