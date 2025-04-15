from sqlalchemy import text
import pandas as pd
import json
from .db_utils import get_engine
from .comms import get_user_approval

__all__ = [
    "fetch_data_from_db",
    "get_all_schemata",
    "get_table_columns_fks",
    "get_db_toolkit",
    "confirm_add_tables",
]


def get_db_toolkit():
    return {
        "get_all_schemata": get_all_schemata,
        "get_table_columns_fks": get_table_columns_fks,
        "fetch_data_from_db": fetch_data_from_db,
        "confirm_add_tables": confirm_add_tables,
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
        print(df)
        if df.empty:
            return "No data found"
        else:
            # Convert DataFrame to JSON string to make it serializable
            print(df)
            return df, "Data fetched successfully"

    except Exception as e:
        return f"Error: {e}"


def get_all_schemata():
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
        query = """
            SELECT 
                table_schema AS schema_name,
                table_name,
                column_name,
                data_type
            FROM 
                INFORMATION_SCHEMA.COLUMNS
            WHERE 
                table_schema NOT IN ('pg_catalog', 'pg_toast', 'information_schema')
            ORDER BY 
            table_schema, 
            table_name, 
            ordinal_position;
        """
        df = pd.read_sql(text(query), engine)
        print(df)
        return df.to_json(orient="records")
    except Exception as e:
        return f"Error: {e}"


def get_table_columns_fks(table_name: str, schema: str):
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
        column_query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}' AND table_schema = '{schema}'"
        fk_query = f"""
            SELECT
                tc.table_schema, 
                tc.constraint_name, 
                tc.table_name, 
                kcu.column_name, 
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema='{schema}'
                AND tc.table_name='{table_name}';
        """       

        df_columns = pd.read_sql(text(column_query), engine)
        df_fks = pd.read_sql(text(fk_query), engine)
        print(df_columns)
        print(df_fks)
        if df_columns.empty:
            return "No schema found"
        else:
            # Combine both dataframes into a single JSON object
            print(json.dumps({
                "columns": json.loads(df_columns.to_json(orient="records")),
                "foreign_keys": json.loads(df_fks.to_json(orient="records"))
            }))
            return json.dumps({
                "columns": json.loads(df_columns.to_json(orient="records")),
                "foreign_keys": json.loads(df_fks.to_json(orient="records"))
            })

    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"


def confirm_add_tables(table_names: str):
    """Verifies that the table names are valid and exist in the database.

    Args:
        table_names (list[str]): List of table names

    Returns:
        str: User approval message along with neccessary context for the agent or feedback for the agent

    Raises:
        Exception: If database connection fails or query execution fails
    """
    rsp, feedback = get_user_approval(table_names)
    return rsp, feedback
