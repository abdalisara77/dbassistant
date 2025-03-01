import os
from dotenv import load_dotenv
from openai import OpenAI
import time
import json
from .baseAssistant import BaseAssistant, baseAssistantEventHandler, client
from typing_extensions import override  
from .db_tools import *
from .llm_utils import * 
import pandas as pd

class dbAssistantEventHandler(baseAssistantEventHandler):
    def __init__(self, tool_dict, name):
        super().__init__(tool_dict, name)
        self.name = name
        self.toolkit = tool_dict
    
    @override
    def handle_requires_action(self, data, run_id):
        tool_outputs = []
        toolkit = self.toolkit
        for tool in data.required_action.submit_tool_outputs.tool_calls:
            function_name = tool.function.name
            function_args = tool.function.arguments
            
            if function_name in toolkit.keys():
                try:
                    result = invoke_tool_for_llm(toolkit[function_name], function_args)
                    if function_name == "fetch_data_from_db": 
                        try:
                            data, msg = result
                            print(data)
                            #Check if data is a DataFrame and convert it to CSV for file creation
                            if isinstance(data, pd.DataFrame):
                                try:
                                    temp_file = data.to_csv('temp.csv', index=False)
                                    file = client.files.create(file=open("temp.csv", "rb"), purpose='assistants')
                                    print(f"File uploaded successfully. File ID: {file.id}")
                                except FileNotFoundError:
                                    print(f"Error: File not found at path '{temp_file}'")
                                except Exception as e:
                                    print(f"API Error: {str(e)}")
                                
                                current_thread = client.beta.threads.retrieve(thread_id=self.current_run.thread_id)
                                curr_thread_resources = current_thread.tool_resources.code_interpreter.file_ids 
                                curr_thread_resources = curr_thread_resources + [file.id]
                                client.beta.threads.update(thread_id=self.current_run.thread_id, tool_resources={"code_interpreter": {"file_ids": curr_thread_resources}})
                            msg = f"Query ran successfully. The results are stored in the file {file.id}. Please use code to access the file."
                            tool_outputs.append({"tool_call_id": tool.id, "output": encode_func_call_result(msg)})
                        except Exception as e:
                            tool_outputs.append({"tool_call_id": tool.id, "output": encode_func_call_result(f"Error: {str(e)}")})
                    else: 
                        try:
                            serialized = json.dumps(result)
                            tool_outputs.append({"tool_call_id": tool.id, "output": encode_func_call_result(result)})
                        except TypeError:
                            tool_outputs.append({"tool_call_id": tool.id, "output": encode_func_call_result(str(result))})
                except Exception as e:
                    tool_outputs.append({"tool_call_id": tool.id, "output": encode_func_call_result(f"Error: {str(e)}")})
            else:
                tool_outputs.append({"tool_call_id": tool.id, "output": encode_func_call_result(f"Error: Tool {function_name} not found")})
        
        self.submit_tool_outputs(tool_outputs, run_id)
        

    @override
    def submit_tool_outputs(self, tool_outputs, run_id):
        curr_event_handler = dbAssistantEventHandler(self.toolkit, self.name)
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