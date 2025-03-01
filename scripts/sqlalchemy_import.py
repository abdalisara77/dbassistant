from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Float, DateTime, Date
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DB_URI")
folder_path = os.getenv("FOLDER_PATH")

def get_sql_type(dtype):
    """Map pandas dtypes to SQLAlchemy types"""
    if 'int' in str(dtype):
        return Integer
    elif 'float' in str(dtype):
        return Float
    elif 'datetime' in str(dtype):
        return DateTime
    elif 'date' in str(dtype):
        return Date
    else:
        return String(255)

def sanitize_column_name(name):
    """Sanitize column names to be SQL-friendly"""
    sanitized = name.replace(' ', '_').replace('%', 'percent')
    # Remove any other non-alphanumeric characters except underscore
    sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '_')
    return sanitized.lower()

def create_table_from_csv(engine, csv_file):
    """Dynamically create a table based on CSV structure"""
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        raise
    
    # convert all NaN to None
    df = df.replace({pd.NA: None, float('nan'): None})[1:]
    
    # Get the base filename without extension to use as table name
    table_name = Path(csv_file).stem
    
    # Create MetaData instance
    metadata = MetaData()
    
    # Create a mapping of original to sanitized column names
    column_mapping = {col: sanitize_column_name(col) for col in df.columns}
    
    # Rename DataFrame columns
    df = df.rename(columns=column_mapping)
    
    # Create table with columns based on DataFrame structure
    columns = []
    pkeys = {
        'workouts': ['Cycle start time', 'Cycle start end', 'Cycle timezone', 'Workout start time', 'Workout end time'],
        'sleeps': ['Cycle start time', 'Cycle end time', 'Cycle timezone', 'Sleep onset', 'Wake onset'],
        'physiological_cycles': ['Cycle start time', 'Cycle end time', 'Cycle timezone'],
        'journal_entries': ['Cycle start time', 'Cycle end time', 'Cycle timezone', 'Question text'], 
    }
    
    # Sanitize the primary key names in the pkeys dictionary
    sanitized_pkeys = {
        table: [sanitize_column_name(col) for col in cols]
        for table, cols in pkeys.items()
    }
    
    for column_name, dtype in df.dtypes.items():
        sql_type = get_sql_type(dtype)
        # column_name is already sanitized here
        if column_name in sanitized_pkeys.get(table_name, []):
            columns.append(Column(column_name, sql_type, primary_key=True))
        else:
            columns.append(Column(column_name, sql_type))
    
    # Create the table
    table = Table(table_name, metadata, *columns)
    
    # Create the table in the database
    try:
        metadata.create_all(engine)
    except Exception as e:
        raise
    
    return table, df

def import_csv_data(engine, csv_files):
    """Import data from CSV files into dynamically created tables"""
    for csv_file in csv_files:
        try:
            # Create table and get DataFrame
            table, df = create_table_from_csv(engine, csv_file)
            
            # Convert DataFrame to dictionary format
            records = df.to_dict('records')
            
            # Insert data
            with engine.connect() as conn:
                for i, record in enumerate(records):
                    try:
                        stmt = table.insert().values(**record)
                        conn.execute(stmt)
                    except Exception:
                        # Continue with next record
                        pass
                conn.commit()
        except Exception:
            # Continue with next file
            pass

if __name__ == "__main__":
    print("Starting data import process")
    data_folder = folder_path
    
    csv_files = []
    for file in os.listdir(data_folder):
        if file.endswith(".csv"):
            csv_files.append(os.path.join(data_folder, file))
    
    print(f"Found {len(csv_files)} CSV files to import")
    
    # Setup database and import data
    try:
        engine = create_engine(db_url)
        import_csv_data(engine, csv_files)
        print("Data import completed successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise   