# 🤖 SQL Agent — Natural Language Querying for Databases

A powerful **SQL Agent** built using:

- **Streamlit** (UI)
- **LangChain SQL Agent**
- **Ollama LLMs (llama3 / phi3 / mistral)**
- **PostgreSQL OR SQLite**

The agent allows users to:

✔ Ask natural language questions about any SQL database  
✔ Automatically generate SQL queries  
✔ Execute them safely  
✔ Return clean, readable results  
✔ Display the full database schema  

---

## 🚀 Features

### 🧠 Natural-language SQL reasoning  
The agent converts English questions → optimized SQL queries.

### 🔍 Automatic schema understanding  
Reads your schema, tables, and columns dynamically.

### 📊 Clean typed results  
Tabular output via Pandas.

### ⚙ Configurable LLM  
Supports llama3, llama2, mistral, codellama, phi3.

### 🧩 Supports PostgreSQL & SQLite  
Switch instantly by changing `DATABASE_URL`.

---

## 🏗 Project Structure

sql_agent_clean/
│
├── app/
│ └── agent.py # backend agent logic
│
├── ui/
│ └── sql_agent_ui.py # Streamlit UI
│
├── db/
│ ├── sample.db # optional demo DB
│ └── schema.sql # schema definition
│
├── .env.example
├── requirements.txt
├── .gitignore
└── README.md

yaml
Copy code

---

## 📦 Installation

### 1️⃣ Clone repo

```bash
git clone https://github.com/<your username>/sql-agent.git
cd sql_agent_clean
2️⃣ Create virtual env
bash
Copy code
python -m venv .venv
.\.venv\Scripts\activate
3️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
▶️ Run the SQL Agent
bash
Copy code
streamlit run ui/sql_agent_ui.py
⚙ Environment Variables
Copy .env.example → .env

ini
Copy code
DATABASE_URL=postgresql://user:password@localhost:5432/db
LLM_MODEL=llama3
MAX_ITERATIONS=5
🧪 Example Questions
How many tables are in this database?

Show me the schema of the customers table.

How many orders were placed in March?

List all products priced above 500.

🛠 Tech Stack
Component	Library
UI	Streamlit
LLM	Ollama
Agent	LangChain SQL Agent
DB	PostgreSQL / SQLite

📌 Future Enhancements
Add query validation layer

Add RAG-enhanced SQL agent

Streamlit Chat History export

Multi-database switching

🤝 Contributing
PRs welcome!
Contact: Keval Ahir

yaml
Copy code

---

# ✅ NEXT STEPS FOR YOU

Now run:

```powershell
ls C:\Users\keval\Desktop\sql_agent_clean