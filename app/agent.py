from langchain_community.utilities import SQLDatabase
from langchain_community.llms import Ollama
from langchain_community.agent_toolkits import create_sql_agent

SAFE_SQL_PROMPT = """
You are an expert PostgreSQL SQL agent.

RULES:
- Generate ONLY SELECT queries
- NEVER use INSERT, UPDATE, DELETE, DROP, ALTER
- Use only tables and columns from the schema
- If the question cannot be answered, say so clearly
- After executing SQL, explain the result in simple language
"""

class SQLAgentService:
    def __init__(self, db_url: str, model_name: str, max_iterations: int = 5):
        self.db_url = db_url
        self.model_name = model_name
        self.max_iterations = max_iterations
        self.db = None
        self.agent = None

    def initialize(self):
        self.db = SQLDatabase.from_uri(self.db_url)

        llm = Ollama(
            model=self.model_name,
            temperature=0,
            num_ctx=2048,
            num_predict=256
        )

        schema_info = self.db.get_table_info()

        system_prompt = f"""
{SAFE_SQL_PROMPT}

Database schema:
{schema_info}
"""

        self.agent = create_sql_agent(
            llm=llm,
            db=self.db,
            prefix=system_prompt,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=self.max_iterations,
            early_stopping_method="force",
            top_k=10
        )

    def run(self, question: str) -> str:
        if not self.agent:
            raise RuntimeError("Agent not initialized")
        return self.agent.run(question)

    def get_schema(self) -> str:
        return self.db.get_table_info()
