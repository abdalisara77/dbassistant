from modules.base_assistant import BaseAssistant
from modules.converse import Converse
from modules.db_thread import DbThread
from modules.db_tools import get_db_toolkit
from modules.context_utils import get_dbexplorer_context_toolkit


def run_dbexplorer():
    """Run the database explorer in an interactive loop.

    This function initializes the explorer with the necessary tools and configuration,
    then enters an interactive loop where the user can input messages and receive responses.
    """

    db_toolkit = get_db_toolkit()
    context_toolkit = get_dbexplorer_context_toolkit()
    
    assistant = BaseAssistant(
        name="Data Explorer",
        instruct_file="instructions/db_explorer_instructs.txt",
        tools= db_toolkit | context_toolkit,
        builtin_tools=[],
        model="gpt-4.1",
        tool_resources=None,
    )

    dbthread = DbThread(tool_resources=None)
    dbthread.create_db_thread()

    conversation = Converse(assistant, dbthread)
    conversation.init_conversation()


if __name__ == "__main__":
    run_dbexplorer()
