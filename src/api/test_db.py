from sqlalchemy import create_engine
from models import Base
from config import DATABASE_URL

def test_connection():
    try:
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(engine)
        print("Database connection successful!")
        print("Tables created!")
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    test_connection() 