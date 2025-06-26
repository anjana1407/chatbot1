import streamlit as st
import time
import json
import os

# Handle OpenAI import with detailed error reporting
try:
    import openai
    st.success(" OpenAI imported successfully")
except ImportError as e:
    st.error(f"Failed to import OpenAI: {str(e)}")
    st.error("Make sure 'openai' is in your requirements.txt file")
    st.stop()
except Exception as e:
    st.error(f" Unexpected error importing OpenAI: {str(e)}")
    st.stop()

# Handle email_tool import
try:
    from email_tool import send_email
    st.success(" Email tool imported successfully")
except ImportError as e:
    st.error(f" Failed to import email_tool: {str(e)}")
    st.info("Creating a fallback email function...")
    
    def send_email(to, subject, body):
        return f"Email simulation: Sent to {to} with subject '{subject}'"

# Initialize the OpenAI client
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def setup_assistant():
    try:
        assistant = client.beta.assistants.create(  
            name="Context AI Assistant",
            instructions="""You are a helpful assistant that answers questions ONLY based on the training content provided by the user. 

IMPORTANT RULES:
1. If the user's question can be answered using the training content, provide a helpful answer.
2. If the user's question is outside the scope of the training content, respond EXACTLY with: "I'm sorry, I can only answer questions based on the provided training content."
3. Always stay within the bounds of the provided context.
4. Do not use your general knowledge - only use the training content provided.""",
            model="gpt-4o-mini",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "send_email",
                        "description": "Simulates sending an email to a user.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "to": {
                                    "type": "string", 
                                    "description": "Email address to send to"
                                },
                                "subject": {
                                    "type": "string", 
                                    "description": "Email subject line"
                                },
                                "body": {
                                    "type": "string", 
                                    "description": "Email body content"
                                }
                            },
                            "required": ["to", "subject", "body"]
                        }
                    }
                }
            ]
        )
        
        return assistant.id, None
        
    except Exception as e:
        st.error(f"Error creating assistant: {str(e)}")
        return None, None

def get_response(question, assistant_id, file_id=None):
    try:
        # Check if context file exists
        try:
            with open("context.txt", "r", encoding="utf-8") as f:
                context_content = f.read().strip()
        except FileNotFoundError:
            return "No training content found. Please save some context first."
        
        if not context_content:
            return "No training content available. Please add some training content first."
        
        # Create a new thread
        thread = client.beta.threads.create()
        
        # Prepare the message with context
        message_content = f"""Training Content:
========================================
{context_content}
========================================

User Question: {question}

Please answer the above question using ONLY the training content provided above. If the question cannot be answered from the training content, respond with: "I'm sorry, I can only answer questions based on the provided training content."
"""
        
        # Add message to thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message_content
        )
        
        # Create and run the assistant
        run = client.beta.threads.runs.create(
            assistant_id=assistant_id,
            thread_id=thread.id
        )
        
        # Poll for completion
        max_attempts = 30
        attempts = 0
        
        while attempts < max_attempts:
            try:
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=thread.id, 
                    run_id=run.id
                )
                
                if run_status.status == "requires_action":
                    # Handle function calls
                    tool_outputs = []
                    for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
                        if tool_call.function.name == "send_email":
                            try:
                                args = json.loads(tool_call.function.arguments)
                                result = send_email(
                                    args.get("to", ""), 
                                    args.get("subject", ""), 
                                    args.get("body", "")
                                )
                                tool_outputs.append({
                                    "tool_call_id": tool_call.id,
                                    "output": result
                                })
                            except Exception as e:
                                tool_outputs.append({
                                    "tool_call_id": tool_call.id,
                                    "output": f"Error: {str(e)}"
                                })
                    
                    # Submit tool outputs
                    client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                
                elif run_status.status == "completed":
                    # Get the response
                    messages = client.beta.threads.messages.list(thread_id=thread.id)
                    for message in messages.data:
                        if message.role == "assistant":
                            for content in message.content:
                                if content.type == "text":
                                    return content.text.value
                    return "No response found from assistant."
                
                elif run_status.status == "failed":
                    error_msg = getattr(run_status, 'last_error', 'Unknown error')
                    return f"Assistant failed: {error_msg}"
                
                elif run_status.status in ["cancelled", "expired"]:
                    return f"Assistant run {run_status.status}."
                
                # Continue polling
                time.sleep(1)
                attempts += 1
                
            except Exception as e:
                return f"Error during execution: {str(e)}"
        
        return "Assistant response timed out. Please try again."
        
    except Exception as e:
        return f"Error getting response: {str(e)}"
