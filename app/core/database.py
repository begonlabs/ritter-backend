from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo = settings.DEBUG,
    pool_pre_ping = True,
    pool_recycle = 300,
)

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()



async def get_db():
    """
    Dependency to get a database session.
    Used with FastAPI Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)



async def check_database_connection():
    """Check that the database connection is working"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False