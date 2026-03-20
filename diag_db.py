import psycopg2
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL')
print(f"Testing connection to: {db_url}")

try:
    engine = create_engine(db_url)
    connection = engine.connect()
    print("SQLAlchemy Connection successful!")
    connection.close()
except Exception as e:
    import traceback
    print("Full Error Trace:")
    traceback.print_exc()
