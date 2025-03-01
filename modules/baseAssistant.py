import os
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler
import time
import json
import pandas as pd
from dotenv import load_dotenv
from .llm_utils import invoke_tool_for_llm, encode_func_call_result, func_to_json
from .db_tools import get_db_toolkit
from pathlib import Path


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

class BaseAssistant:
    """Base class for creating and managing OpenAI assistants.
    
    This class provides functionality to create and retrieve assistants with
    specified tools, instructions, and models.
    """
    
    def __init__(self, name, instruct_file, tools, builtin_tools, model, tool_resources): 
        """Initialize a BaseAssistant instance.
        
        Args:
            name (str): The name of the assistant.
            instruct_file (str): Path to the file containing instructions for the assistant.
            tools (dict): Dictionary of custom tools to be used by the assistant.
            builtin_tools (list): List of built-in OpenAI tools to be used.
            model (str): The OpenAI model to use for the assistant.
            tool_resources: Resources for the assistant's tools.
        """
        self.name = name
        self.instruct_file = instruct_file
        self.tools = tools
        self.builtin_tools = builtin_tools
        self.id = None
        self.model = model
        self.tool_resources = tool_resources
        
    def create_assistant(self):
        """Create a new assistant with the specified configuration.
        
        Returns:
            The created assistant object.
            
        Raises:
            Exception: If assistant creation fails.
        """
        json_tools = [func_to_json(tool) for tool in self.tools.values()]
        try:
            with open(self.instruct_file, 'r') as f:
                instructions = f.read()
                
            assistant = client.beta.assistants.create(
                name=self.name,
                instructions=instructions,
                tools=json_tools + self.builtin_tools,
                model=self.model,
            )
            self.id = assistant.id
            return assistant
        except Exception as e:
            raise
    
    def retrieve_assistant(self):
        """Retrieve an existing assistant by ID.
        
        Returns:
            The retrieved assistant object.
            
        Raises:
            Exception: If assistant retrieval fails.
        """
        try:
            assistant = client.beta.assistants.retrieve(self.id)
            return assistant
        except Exception as e:
            raise

class baseAssistantEventHandler(AssistantEventHandler):
    """Event handler for OpenAI assistant interactions.
    
    This class handles events from the OpenAI assistant API, including
    text creation, tool calls, and message processing.
    """
    
    def __init__(self, tool_dict, name):
        """Initialize the event handler.
        
        Args:
            tool_dict (dict): Dictionary of tools available to the assistant.
            name (str): Name of the assistant.
        """
        super().__init__()
        self.toolkit = tool_dict
        self.name = name
        
    @override
    def on_text_created(self, text) -> None:
        """Handle text creation events.
        
        Args:
            text: The created text object.
        """
        print(f"\n {self.name} > ", end="", flush=True)
      
    @override
    def on_text_delta(self, delta, snapshot):
        """Handle text delta events (incremental text updates).
        
        Args:
            delta: The text delta object.
            snapshot: The current text snapshot.
        """
        print(delta.value, end="", flush=True)
      
    @override
    def on_tool_call_created(self, tool_call):
        """Handle tool call creation events.
        
        Args:
            tool_call: The tool call object.
        """
        print(f"\n {self.name} > {tool_call.type}\n", flush=True)
        if tool_call.type == "function":
            print(f"function name: {tool_call.function.name}\n", flush=True)
    
    def on_event(self, event):
        """Handle general events from the assistant.
        
        Args:
            event: The event object.
        """
        if event.event == 'thread.run.requires_action':
            run_id = event.data.id 
            self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
        """Handle events that require action (like tool calls).
        
        Args:
            data: The event data.
            run_id: The ID of the current run.
        """
        tool_outputs = []
        toolkit = self.toolkit
        
        for tool in data.required_action.submit_tool_outputs.tool_calls:
            function_name = tool.function.name
            function_args = tool.function.arguments
            
            if function_name in toolkit:
                try:
                    result = invoke_tool_for_llm(toolkit[function_name], function_args)
                    tool_outputs.append({"tool_call_id": tool.id, "output": encode_func_call_result(result)})
                except Exception as e:
                    tool_outputs.append({"tool_call_id": tool.id, "output": encode_func_call_result(f"Error: {str(e)}")})
            else:
                tool_outputs.append({"tool_call_id": tool.id, "output": encode_func_call_result(f"Error: Tool {function_name} not found")})
        
        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        """Submit tool outputs back to the assistant.
        
        Args:
            tool_outputs (list): List of tool outputs to submit.
            run_id (str): The ID of the current run.
        """
        curr_event_handler = baseAssistantEventHandler(self.toolkit, self.name)
        
        try:
            with client.beta.threads.runs.submit_tool_outputs_stream(
                thread_id=self.current_run.thread_id,
                run_id=self.current_run.id,
                tool_outputs=tool_outputs,
                event_handler=curr_event_handler,
            ) as stream:
                stream.until_done()
                print()
        except Exception as e:
            pass

    @override
    def message_done(self, message):
        """Handle message completion events.
        
        Args:
            message: The completed message object.
        """
        for content in message.content:
            if content.type == "text":
                for annot in content.text.annotations:
                    if annot.type == "file_path":
                        file_id = annot.file_path.file_id
                        
                        try:
                            file_content = client.files.retrieve(file_id)
                            file_type = annot.text.split('.')[-1]
                            
                            downloads_dir = Path(__file__).parent.parent / 'downloads'
                            downloads_dir.mkdir(exist_ok=True)
                                
                            file_path = downloads_dir / f"{file_id}.{file_type}"
                            with open(file_path, "wb") as f:
                                f.write(file_content.file.read())
                        except Exception as e:
                            pass
    
    @override
    def on_tool_call_delta(self, delta, snapshot):
        """Handle tool call delta events.
        
        Args:
            delta: The tool call delta object.
            snapshot: The current tool call snapshot.
        """
        if delta.type == "code_interpreter":
            if delta.code_interpreter.input: 
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)
                    
    @override
    def on_message_done(self, message):
        """Handle message completion events.
        
        This method processes the completed message, handling any images or file paths
        included in the message content.
        
        Args:
            message: The completed message object.
        """
        for content in message.content:
            if hasattr(content, 'image_file') and content.image_file:
                file_id = content.image_file.file_id
                file_content = client.files.content(file_id)
                downloads_dir = Path(__file__).parent.parent / 'downloads'
                downloads_dir.mkdir(exist_ok=True)
                file_path = downloads_dir / f"{file_id}.png"
                with open(file_path, "wb") as f:
                    f.write(file_content.read())
                print(f'Image saved to: {file_path}', flush=True)
            elif content.type == "text":
                if content.text.annotations:
                    for annot in content.text.annotations:
                        if annot.type == "file_path":
                            file_id = annot.file_path.file_id
                            file_content = client.files.content(file_id)
                            file_type = annot.text.split('.')[-1]
                            downloads_dir = Path(__file__).parent.parent / 'downloads'
                            downloads_dir.mkdir(exist_ok=True)
                            file_path = downloads_dir / f"{file_id}.{file_type}"
                            with open(file_path, "wb") as f:
                                f.write(file_content.read()) 
                            print(f'code interpreter returned image with the following path: {file_path}', flush=True)
            
