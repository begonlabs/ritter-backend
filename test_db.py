from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the DATABASE_URL from environment variables
database_url = os.getenv('DATABASE_URL')
print(f"Attempting to connect to database...")
print(f"Database URL: {database_url}")

try:
    # Create engine
    engine = create_engine(database_url)
    
    # Try to connect
    with engine.connect() as connection:
        print("Successfully connected to the database!")
        
except Exception as e:
    print("Failed to connect to the database!")
    print(f"Error: {str(e)}")
