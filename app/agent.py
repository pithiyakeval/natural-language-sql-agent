from langchain_community.utilities import SQLDatabase
from langchain_community.llms import Ollama
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents.agent_types import AgentType

class SQLAgentService:
    def __init__(self, db_url: str, model_name: str, max_iterations: int = 5):
        self.db_url = db_url
        self.model_name = model_name
        self.max_iterations = max_iterations
        self.db = None
        self.agent = None
        self.table_names = []

    def initialize(self):
        self.db = SQLDatabase.from_uri(self.db_url)
        self.table_names = self.db.get_usable_table_names()

        llm = Ollama(model=self.model_name, temperature=0)

        self.agent = create_sql_agent(
            llm=llm,
            db=self.db,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
            max_iterations=self.max_iterations,
            early_stopping_method="force",
            top_k=10
        )

        return True

    def get_table_info(self):
        try:
            return self.db.get_table_info()
        except:
            return f"Available tables: {', '.join(self.table_names)}"
