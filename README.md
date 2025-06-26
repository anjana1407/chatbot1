<h1>Context-Based Chatbot (OpenAI Assistants API)</h1>

This is a Streamlit chatbot that uses OpenAI’s Assistants API to respond only based on user-provided training content. It can also generate and simulate sending emails when asked through the chat.

<h3>Features</h3>

-Loads custom context provided by the user
-Creates an OpenAI Assistant using GPT-4o-mini
-Answers only using the context and nothing outside it
-Responds with a fixed message if the question is outside the context
-Can simulate sending emails via tool call
-Displays chat history in a clean interface
-Supports basic reset and email storage

<h3>How to Run</h3>

-Install dependencies
pip install -r requirements.txt

-Add your OpenAI API key
-Either set an environment variable:
    export OPENAI_API_KEY=your_key_here
    Or add to .streamlit/secrets.toml:
    OPENAI_API_KEY = "your_key_here"
    
-Start the app
streamlit run main.py

<h3>Notes</h3>
-The assistant is created dynamically each time new context is saved
-The context is stored in a local file called context.txt
-Tool calling is used to simulate sending emails with subject and body

