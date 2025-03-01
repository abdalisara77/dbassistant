from sqlalchemy import create_engine, inspect, text
import pandas as pd
import json 
from .db_utils import get_engine

__all__ = ["fetch_data_from_db", "get_all_tables_in_schema", "get_table_columns", "get_db_toolkit"]


def get_db_toolkit():
    return {
        "get_all_tables_in_schema": get_all_tables_in_schema,
        "get_table_columns": get_table_columns,
        "fetch_data_from_db": fetch_data_from_db,
    }


def fetch_data_from_db(query: str, table_name: str, schema: str):
    """Executes a SQL query and returns the results as JSON.
    
    Args:
        query (str): The SQL query to execute
        table_name (str): Name of the table being queried
        schema (str): Database schema name
        
    Returns:
        tuple: (JSON string of results, status message) or error message string
        
    Raises:
        Exception: If database connection fails or query execution fails
    """
    engine = get_engine()
    if engine is None:
        return "Error: Unable to connect to the database"
    
    try:
        # Clean up the query and ensure it's a proper SELECT
        df = pd.read_sql(text(query), engine)
        
        if df.empty:
            return "No data found" 
        else:
            # Convert DataFrame to JSON string to make it serializable
            return df, "Data fetched successfully"
        
    except Exception as e:
        return f"Error: {e}"
    

def get_all_tables_in_schema(schema: str):
    """Retrieves all table names from a specified schema.
    
    Args:
        schema (str): Name of the database schema
        
    Returns:
        tuple: (JSON string of table names, status message) or error message string
        
    Raises:
        Exception: If database connection fails or query execution fails
    """
    engine = get_engine()
    if engine is None:
        return "Error: Unable to connect to the database"
    
    try:
        query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'"
        
        df = pd.read_sql(text(query), engine)
        
        if df.empty:
            return "No tables found"
        else:
            return df.to_json(orient="records"), "Tables fetched successfully"
        
    except Exception as e:
        return f"Error: {e}"
    

def get_table_columns(table_name: str, schema: str):
    """Retrieves column information for a specified table.
    
    Args:
        table_name (str): Name of the table
        schema (str): Name of the database schema
        
    Returns:
        str: JSON string of column information or error message
        
    Raises:
        Exception: If database connection fails or query execution fails
    """
    engine = get_engine()
    if engine is None:
        return "Error: Unable to connect to the database"
    
    try:
        query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}' AND table_schema = '{schema}'"
        
        df = pd.read_sql(text(query), engine)
        
        if df.empty:
            return "No schema found"
        else:
            return df.to_json(orient="records")
        
    except Exception as e:
        return f"Error: {e}"
    


