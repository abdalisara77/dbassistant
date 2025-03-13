from modules.baseAssistant import BaseAssistant, client
from modules.dbAssistant import dbAssistantEventHandler
from modules.dbThread import dbThread
from modules.db_tools import *
from modules.llm_utils import *


def run_assistant():
    """Run the database assistant in an interactive loop.

    This function initializes the assistant with the necessary tools and configuration,
    then enters an interactive loop where the user can input messages and receive responses.
    """
    toolkit = get_db_toolkit()
    builtin_tools = [{"type": "code_interpreter"}]

    assistant = BaseAssistant(
        name="Data Expert",
        instruct_file="instructions/db_instructs.txt",
        tools=toolkit,
        builtin_tools=builtin_tools,
        model="gpt-4o",
        tool_resources=None,
    )

    dbexpert = assistant.create_assistant()
    dbthread = dbThread(tool_resources=None)
    thread = dbthread.create_db_thread()

    while True:
        message = input("\n You: ")
        if message == "exit":
            break

        client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=message
        )

        dbeh = dbAssistantEventHandler(
            tool_dict=toolkit, name="Data Expert", thread_obj=dbthread
        )

        with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=dbexpert.id,
            event_handler=dbeh,
        ) as stream:
            stream.until_done()


if __name__ == "__main__":
    run_assistant()
