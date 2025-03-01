import os
import dotenv
from sqlalchemy import create_engine
import pandas as pd

dotenv.load_dotenv()

def get_engine():
    db_uri = os.getenv("DB_URI")
    try: 
        return create_engine(db_uri)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
