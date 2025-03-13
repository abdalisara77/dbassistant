import os
from openai import OpenAI
import json
import pandas as pd
from dotenv import load_dotenv
from .llm_utils import create_context_for_tables
from .db_tools import confirm_add_tables


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)


class dbThread:
    def __init__(self, tool_resources):
        self.tool_resources = tool_resources
        self.thread_id = None
        self.thread_obj = None
        self.tables = []

    def create_db_thread(self):
        self.thread_obj = client.beta.threads.create()
        self.thread_id = self.thread_obj.id
        return self.thread_obj

    def add_tables_to_thread(self, tables):
        print(f"Adding table: {tables} to thread")
        self.tables = self.tables + tables
        return

    def invoke_function(self, func, args):
        """Invoke a function and return the result as a JSON string.
        Args:
            func: The function to invoke
            args: Arguments to pass to the function
        """
        print(f"Invoking function: {func.__name__} with args: {args}")
        args_dict = json.loads(args)
        if func.__name__ == "confirm_add_tables":
            rsp, tables = confirm_add_tables(**args_dict)
            print(rsp, tables)
            if rsp == "success" or rsp == "modified":
                print(f"Adding tables: {tables.split(',')} to thread")
                self.add_tables_to_thread(tables.split(","))
                context = create_context_for_tables(tables.split(","))
                return "tables successfully added" + context

            else:
                return tables
        else:
            return func(**args_dict)

