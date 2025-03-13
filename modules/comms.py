import os
from dotenv import load_dotenv

load_dotenv()


def get_user_approval(table_names: str):
    """Get user approval for adding tables to memory.
    
    Args:
        table_names (str): Comma-separated list of table names

    Returns:
        tuple: (response, feedback)
        response (str): 'y' if approved, 'n' if not approved, 'm' if modified
        feedback (str): Feedback message from the user
    """
    print("inside get_user_approval") 
    print(table_names)
    while True:
        print(f"The following tables will be added to the thread's memory: {table_names}")
        response = input("Do you approve? (y/n/m): ").lower()
        if response == 'y':
            return 'success', table_names
        elif response == 'n':
            # ask for feedback 
            feedback = input("Why would you reject my hard work: ") 
            return 'failure', feedback
        elif response == 'm':
            new_tables = input("Modify the tables as you see fit: ")
            return 'modified', new_tables
        else:
            print("Invalid response. Please enter 'y', 'n', or 'm'.")





