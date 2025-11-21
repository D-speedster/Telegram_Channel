import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from data.database.db_manager import DBManager
from data.database.models import Admin
from src.config import ADMIN_IDS

def initialize_database():
    """Initializes the database, creates tables, and populates initial data."""
    db = DBManager()

    print("Creating database tables...")
    db.create_tables()

    # --- Populate Initial Data ---

    # Add default post types
    print("\nAdding default post types...")
    default_post_types = ['text', 'photo', 'video', 'document', 'audio', 'sticker', 'animation']
    for post_type in default_post_types:
        db.add_post_type(post_type)

    # Add admin users from config
    print("\nAdding admin users from config...")
    if not ADMIN_IDS:
        print("No admin IDs found in the config. Skipping admin population.")
    else:
        for admin_id in ADMIN_IDS:
            existing_admin = db.db_session.query(Admin).filter_by(user_id=admin_id).first()
            if not existing_admin:
                new_admin = Admin(user_id=admin_id, username=f"Admin_{admin_id}") # Placeholder username
                db.db_session.add(new_admin)
                print(f"Admin with user_id {admin_id} added.")
            else:
                print(f"Admin with user_id {admin_id} already exists.")
        db.db_session.commit()

    # Close the session
    db.close_session()

    print("\nDatabase initialization complete!")

if __name__ == "__main__":
    # A simple confirmation before proceeding
    confirm = input("Are you sure you want to initialize the database? This will create tables and add default data. (y/n): ")
    if confirm.lower() == 'y':
        initialize_database()
    else:
        print("Database initialization cancelled.")