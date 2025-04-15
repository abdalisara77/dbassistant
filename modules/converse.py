from modules.baseAssistant import client, BaseAssistant
from modules.dbAssistant import dbAssistantEventHandler
from modules.dbThread import dbThread


class Converse:
    """Class to handle the conversation with the assistant."""
    def __init__(self, assistant, thread):
        self.assistant = assistant
        self.thread = thread

    
    def init_conversation(self):
        print("Hello, I'm your data analyst. How can I help you?", flush=True)
        self.assistant.create_assistant()
        self.continue_conversation()

    
    def continue_conversation(self):
        while True:
            message = input("\n You: ")
            if message == "exit":
                break
            
            client.beta.threads.messages.create(
                thread_id=self.thread.thread_id, role="user", content=message
            )

            dbeh = dbAssistantEventHandler(
                tool_dict=self.assistant.tools, name=self.assistant.name, thread_obj=self.thread
            )

            with client.beta.threads.runs.stream(
                thread_id=self.thread.thread_id,
                assistant_id=self.assistant.id,
                event_handler=dbeh,
            ) as stream:
                stream.until_done()
    
