import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def create_vec_store_from_folder(folder_path):
    """
    Create a vector store from a folder of files.
    """
    # Get all files in the folder
    files = os.listdir(folder_path)

    # Create a vector store
    vec_store = client.beta.vector_stores.create(
        name="My Vector Store",
        files=files,
        metadata=[{"file_name": file} for file in files],
    )
