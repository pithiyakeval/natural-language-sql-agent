import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_community.llms import Ollama
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents.agent_types import AgentType
import pandas as pd
import time
import re

# Set up the page
st.set_page_config(
    page_title="SQL Query Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'db_connected' not in st.session_state:
    st.session_state.db_connected = False
if 'db' not in st.session_state:
    st.session_state.db = None
if 'table_names' not in st.session_state:
    st.session_state.table_names = []

# Sidebar for configuration
with st.sidebar:
    st.title("Configuration")
    st.subheader("Database Connection")
    
    db_url = st.text_input(
        "Database URL",
        # value="postgresql://postgres:5141@localhost:5432/chatbot_db",
        value = "postgresql://meghamrut_dev_db_user:dev_user@localhost:5432/meghamrut_dev_db",
        help="Format: postgresql://username:password@host:port/database"
    )
    
    st.subheader("LLM Settings")
    model_name = st.selectbox(
        "Ollama Model",
        options=["llama3", "llama2", "mistral", "codellama", "phi3"],
        index=0
    )
    
    # Add max iterations setting to prevent agent from running too long
    max_iterations = st.slider("Max Agent Iterations", min_value=3, max_value=15, value=5, 
                              help="Limit the number of reasoning steps to prevent long runs")
    
    if st.button("Initialize Agent"):
        with st.spinner("Connecting to database and initializing agent..."):
            try:
                # Initialize database connection
                st.session_state.db = SQLDatabase.from_uri(db_url)
                
                # Get table names for quick access
                st.session_state.table_names = st.session_state.db.get_usable_table_names()
                
                # Initialize LLM
                llm = Ollama(model=model_name, temperature=0)
                
                # Create agent with the correct agent type
                st.session_state.agent = create_sql_agent(
                    llm=llm,
                    db=st.session_state.db,
                    verbose=True,
                    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                    handle_parsing_errors=True,
                    max_iterations=max_iterations,  # Limit iterations to prevent long runs
                    early_stopping_method="force",
                    top_k=10
                )
                
                st.session_state.db_connected = True
                st.success("Agent initialized successfully!")
                
                # Try to get database schema for display
                try:
                    table_info = st.session_state.db.get_table_info()
                    st.session_state.table_info = table_info
                except Exception as e:
                    st.warning(f"Could not retrieve full schema details: {str(e)}")
                    st.session_state.table_info = f"Available tables: {', '.join(st.session_state.table_names)}"
                    
            except Exception as e:
                st.error(f"Error initializing agent: {str(e)}")
                st.session_state.db_connected = False

# Function to clean up the agent response
def clean_agent_response(response):
    # If the response is a list with a tuple (like the SQL result)
    if isinstance(response, list) and len(response) > 0:
        if isinstance(response[0], tuple) and len(response[0]) > 0:
            # Format the result as a table if it has multiple columns
            if len(response[0]) > 1:
                df = pd.DataFrame(response)
                return df.to_markdown(index=False)
            else:
                # Single value result
                return str(response[0][0])
    
    # Handle string responses
    if isinstance(response, str):
        # Remove unnecessary prefixes and suffixes
        response = re.sub(r'^Answer:\s*', '', response)
        response = re.sub(r'\s*I don\'t know.*$', '', response, flags=re.IGNORECASE)
        response = re.sub(r'\s*I cannot.*$', '', response, flags=re.IGNORECASE)
        response = re.sub(r'\s*Let me.*$', '', response, flags=re.IGNORECASE)
        
        # If the response seems to contain SQL, try to extract just the answer
        if 'SELECT' in response and '```' in response:
            # Extract content between ```sql and ```
            sql_match = re.search(r'```sql(.*?)```', response, re.DOTALL)
            if sql_match:
                # If there's text after the SQL, include it
                parts = response.split('```')
                if len(parts) > 2 and parts[2].strip():
                    return parts[2].strip()
    
    return str(response).strip()

# Function to handle simple queries without using the agent
def handle_simple_query(question):
    """Handle simple queries directly without using the agent"""
    question_lower = question.lower()
    
    # Table count queries
    if "how many table" in question_lower or "total table" in question_lower:
        return f"There are {len(st.session_state.table_names)} tables in the database: {', '.join(st.session_state.table_names)}"
    
    # List tables queries
    if "list table" in question_lower or "name of all table" in question_lower or "what table" in question_lower:
        return f"The database contains these tables: {', '.join(st.session_state.table_names)}"
    
    # Table schema queries
    if "schema" in question_lower:
        for table_name in st.session_state.table_names:
            if table_name.lower() in question_lower:
                try:
                    table_info = st.session_state.db.get_table_info(table_names=[table_name])
                    return f"Schema for table '{table_name}':\n\n{table_info}"
                except:
                    return f"Could not retrieve schema for table '{table_name}'"
    
    # Row count queries
    if "how many row" in question_lower or "number of record" in question_lower:
        for table_name in st.session_state.table_names:
            if table_name.lower() in question_lower:
                try:
                    result = st.session_state.db.run(f"SELECT COUNT(*) FROM {table_name}")
                    return f"Table '{table_name}' has {result} rows."
                except:
                    return f"Could not count rows in table '{table_name}'"
    
    return None

# Main content area
st.title("🤖 SQL Query Agent with Llama 3")
st.markdown("Ask natural language questions about your database and get answers!")

# Display database schema if available
if st.session_state.db_connected and 'table_info' in st.session_state:
    with st.expander("View Database Schema"):
        st.text(st.session_state.table_info)

# Chat interface
if st.session_state.agent and st.session_state.db_connected:
    # Display chat history
    for i, (question, answer, execution_time) in enumerate(st.session_state.history):
        with st.chat_message("user"):
            st.markdown(question)
        
        with st.chat_message("assistant"):
            st.markdown(answer)
            st.caption(f"Execution time: {execution_time:.2f} seconds")
    
    # Input for new question
    question = st.chat_input("Ask a question about your database...")
    
    if question:
        # Add user question to history and display
        st.session_state.history.append((question, "", 0))
        
        with st.chat_message("user"):
            st.markdown(question)
        
        # Get agent response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            start_time = time.time()
            try:
                # First try to handle simple queries directly
                simple_answer = handle_simple_query(question)
                
                if simple_answer:
                    answer = simple_answer
                    execution_time = time.time() - start_time
                else:
                    # Use the agent for complex queries with a simpler prompt
                    response = st.session_state.agent.run(question)
                    answer = clean_agent_response(response)
                    execution_time = time.time() - start_time
                
                # Update history
                st.session_state.history[-1] = (question, answer, execution_time)
                
                # Display response
                message_placeholder.markdown(answer)
                st.caption(f"Execution time: {execution_time:.2f} seconds")
                
            except Exception as e:
                # Calculate execution time even on error
                execution_time = time.time() - start_time
                
                error_msg = f"An error occurred: {str(e)}"
                # Check if it's an iteration limit error
                if "iteration" in str(e).lower() or "limit" in str(e).lower():
                    error_msg += ". Try simplifying your question or increasing the max iterations in settings."
                
                message_placeholder.markdown(f"❌ {error_msg}")
                st.session_state.history[-1] = (question, f"Error: {str(e)}", execution_time)
    
    # Add clear history button
    if st.sidebar.button("Clear History"):
        st.session_state.history = []
        st.rerun()
        
else:
    st.info("Please configure and initialize the agent in the sidebar to get started.")
    
    # Example questions
    st.subheader("Example questions you can ask:")
    st.markdown("""
    - How many tables are in the database?
    - What are the names of all tables?
    - Show me the schema of the customers table
    - How many records are in the orders table?
    - List all customers from London (if you have a customers table)
    - What's the average price of products?
    """)
    
# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Built with [LangChain](https://langchain.com), [Ollama](https://ollama.com), and [Streamlit](https://streamlit.io)")