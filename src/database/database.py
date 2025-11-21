from sqlalchemy.orm import Session
from src.database.models import PostType, PostLog, SessionLocal
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class DBManager:
    def __init__(self):
        self.db: Session = SessionLocal()

    def get_post_types(self) -> List[PostType]:
        try:
            return self.db.query(PostType).all()
        except Exception as e:
            logger.error(f"Error fetching post types: {e}")
            return []

    def add_post_type(self, name: str, banner_file: Optional[str] = None) -> bool:
        try:
            existing = self.db.query(PostType).filter(PostType.name == name).first()
            if existing:
                return False
            new_post_type = PostType(name=name, banner_file=banner_file)
            self.db.add(new_post_type)
            self.db.commit()
            self.db.refresh(new_post_type)
            return True
        except Exception as e:
            logger.error(f"Error adding post type: {e}")
            self.db.rollback()
            return False

    def delete_post_type(self, type_name: str) -> bool:
        try:
            post_type = self.db.query(PostType).filter(PostType.name == type_name).first()
            if post_type:
                self.db.delete(post_type)
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting post type: {e}")
            self.db.rollback()
            return False

    def add_post_log(self, post_type_name: str, text: str, sent_by: int, media_path: Optional[str] = None):
        try:
            post_type = self.db.query(PostType).filter(PostType.name == post_type_name).first()
            if not post_type:
                logger.error(f"Post type '{post_type_name}' not found.")
                return

            new_log = PostLog(
                post_type_id=post_type.id,
                text=text,
                media_path=media_path,
                sent_by=sent_by
            )
            self.db.add(new_log)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error adding post log: {e}")
            self.db.rollback()

    def close(self):
        """Explicitly close the database session."""
        if self.db:
            self.db.close()

    def __del__(self):
        self.close()