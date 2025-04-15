from modules.baseAssistant import BaseAssistant, client
from modules.converse import Converse
from modules.dbThread import dbThread
from modules.db_tools import get_db_toolkit
from modules.context_utils import get_dbassistant_context_toolkit

def run_assistant():
    """Run the database assistant in an interactive loop.

    This function initializes the assistant with the necessary tools and configuration,
    then enters an interactive loop where the user can input messages and receive responses.
    """
    toolkit = get_db_toolkit() | get_dbassistant_context_toolkit()
    builtin_tools = [{"type": "code_interpreter"}]

    assistant = BaseAssistant(
        name="Data Expert",
        instruct_file="instructions/db_assistant_instructs.txt",
        tools=toolkit,
        builtin_tools=builtin_tools,
        model="gpt-4.1",
        tool_resources=None,
    )

    dbthread = dbThread(tool_resources=None)
    dbthread.create_db_thread()

    conversation = Converse(assistant, dbthread)
    conversation.init_conversation()



if __name__ == "__main__":
    run_assistant()
