import streamlit as st
import time
from langchain_community.utilities import SQLDatabase
from langchain_ollama import OllamaLLM
import re

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Business SQL Agent",
    page_icon="📊",
    layout="wide"
)

# =========================
# SESSION STATE
# =========================
if "db" not in st.session_state:
    st.session_state.db = None
if "schema" not in st.session_state:
    st.session_state.schema = None
if "llm" not in st.session_state:
    st.session_state.llm = None
if "ready" not in st.session_state:
    st.session_state.ready = False
if "history" not in st.session_state:
    st.session_state.history = []

# =========================
# RESULT HELPERS
# =========================


def scalar(res):
    if isinstance(res, list):
        return res[0][0]
    if isinstance(res, str):
        return float(res.strip("[]() ").split(",")[0])
    return res

def money(v):
    return f"₹{float(scalar(v)):,.2f}"

def percent(v):
    return f"{round(float(scalar(v)), 2)}%"

def execute_sql(db, sql):
    """
    Central SQL executor
    - Logs SQL
    - Executes SQL
    - Returns result
    """
    print("\n================ SQL EXECUTED ================")
    print(sql)
    print("=============================================\n")

    result = db.run(sql)
    return result


# =========================
# FAST KPI + FILTER ROUTER
# =========================
def fast_router(question, db):
    q = question.lower()

    if "how many users" in q:
        sql = "SELECT COUNT(*) FROM users"
        r = execute_sql(db, sql)
        return sql, f"👥 **Total users:** {int(scalar(r))}"

    if "total revenue" in q:
        sql = """
        SELECT SUM(p.selling_price * oi.quantity)
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        """
        r = execute_sql(db, sql)
        return sql, f"💰 **Total revenue:** {money(r)}"
    if "source" in q or "data source" in q:
        sql = "--metadata query (no DB execution)"
        source_info = f"""
📦 **Data Source**
- Database: SQLite
- File: business.db
- Tables: users, orders, order_items, products
- Execution: Direct SQL via SQLAlchemy
- AI Role: SQL generation only (no execution)
"""     
        return sql, source_info
    if "total profit" in q:
        sql = """
        SELECT SUM((p.selling_price - p.cost_price) * oi.quantity)
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        """
        r = execute_sql(db, sql)
        return sql, f"📈 **Total profit:** {money(r)}"

    if "net profit margin" in q:
        sql = """
        SELECT
        (SUM((p.selling_price - p.cost_price) * oi.quantity) * 100.0)
        / SUM(p.selling_price * oi.quantity)
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        """
        r = execute_sql(db, sql)
        return sql, f"📊 **Net profit margin:** {percent(r)}"

    if "from" in q:
     raw_city = q.split("from")[-1]
     city = re.sub(r"[^a-zA-Z ]", "", raw_city).strip().title()

     if not city:
         return None

     sql = f"SELECT name, city FROM users WHERE city='{city}'"
     r = execute_sql(db, sql)
     return sql, f"👥 **Users from {city}:** {r}"


    if "starts with" in q:
        letter = q.split("starts with")[-1].strip()[0]
        sql = f"SELECT name FROM users WHERE name LIKE '{letter}%'"
        r = execute_sql(db, sql)
        return sql, f"🔤 **Names starting with {letter.upper()}:** {r}"

    return None

# =========================
# CRUD ROUTER (WRITE OPS)
# =========================
def crud_router(question, db):
    q = question.lower().strip()

    # ADD USER
    if q.startswith("add user"):
        try:
            name = q.split("name=")[1].split()[0].title()
            city = q.split("city=")[1].split()[0].title()
        except IndexError:
            return None

        sql = f"""
        INSERT INTO users (name, email, city, signup_date)
        VALUES ('{name}', '{name}@mail.com', '{city}', DATE('now'))
        """
        db.run(sql)
        return sql, f"✅ User **{name}** added successfully"

    # DELETE USER
    if q.startswith("delete user"):
        name = q.replace("delete user", "").strip().title()
        sql = f"DELETE FROM users WHERE name = '{name}'"
        db.run(sql)
        return sql, f"🗑️ User **{name}** deleted successfully"

    # UPDATE PRODUCT PRICE
    if q.startswith("update price"):
        try:
            pid = q.split("product_id=")[1].split()[0]
            price = q.split("price=")[1].split()[0]
        except IndexError:
            return None

        sql = f"""
        UPDATE products
        SET selling_price = {price}
        WHERE product_id = {pid}
        """
        db.run(sql)
        return sql, f"✅ Product **{pid}** price updated"

    return None

# =========================
# AI SQL FALLBACK
# =========================
def ai_sql(question, schema, llm):
    prompt = f"""
Generate ONE SQLite SELECT query.
Use ONLY the schema below.
Return ONLY SQL.

Schema:
{schema}

Question:
{question}

SQL:
"""
    response = llm.invoke(prompt)

    # Ollama may return str or object
    if isinstance(response, str):
        return response.strip()

    return response.content.strip()


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.title("⚙️ Setup")

    if st.button("🚀 Initialize System"):
        with st.spinner("Initializing system..."):
            db = SQLDatabase.from_uri(
                "sqlite:///C:/Users/keval/Desktop/sql_agent_clean/app/business.db"
            )
            schema = db.get_table_info()

            llm = OllamaLLM(
                model="phi3",
                temperature=0,
                num_ctx=2048
            )
            llm.invoke("OK")

            st.session_state.db = db
            st.session_state.schema = schema
            st.session_state.llm = llm
            st.session_state.ready = True

            st.success("✅ System ready")

    if st.button("🧹 Clear Chat"):
        st.session_state.history = []
        st.rerun()

        # Sidebar for configuration
with st.sidebar:
    st.title("Configuration")
    st.subheader("Database Connection")
    
    db_url = st.text_input(
        "Database URL",
        # value="postgresql://postgres:5141@localhost:5432/chatbot_db",
        value = "sqlit3/SQL_AGENT_CLEAN/app/business.db",
        help="Format: postgresql://username:password@host:port/database"
    )
    
    st.subheader("LLM Settings")
    model_name = st.selectbox(
        "Ollama Model",
        options=["llama3", "llama2", "mistral", "codellama", "phi3"],
        index=0
    )
    

# =========================
# MAIN UI
# =========================
st.title("📊 Business SQL Agent")
st.markdown("**Natural language → SQL → Database → Answer**")

if st.session_state.ready:
    with st.expander("📘 Database Schema"):
        st.text(st.session_state.schema)

# =========================
# CHAT
# =========================
    if st.session_state.ready:
        for q, a, t in st.session_state.history:
            with st.chat_message("user"):
                st.markdown(q)
            with st.chat_message("assistant"):
                st.markdown(a)
                st.caption(f"⏱ {t:.2f}s")

        question = st.chat_input("Ask a business question...")

        if question:
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                start = time.time()

                result = (
                    crud_router(question, st.session_state.db)
                    or fast_router(question, st.session_state.db)
                )

                if result:
                    sql, answer = result
                else:
                    sql = ai_sql(
                        question,
                        st.session_state.schema,
                        st.session_state.llm
                    )
                    res = st.session_state.db.run(sql)
                    answer = f"{res}"

                elapsed = time.time() - start

                st.markdown(f"""
    **SQL Executed**
    ```sql
    {sql}
    ``python
    **Result**
    {answer}
    """)

                st.caption(f"⏱ {elapsed:.2f}s")

                # Save history
                st.session_state.history.append(
                    (question, answer, elapsed)
                )

else:
    st.info("👈 Click **Initialize System** to start")

# =========================
# FOOTER
# =========================
st.sidebar.markdown("---")
st.sidebar.markdown("SQLite + Ollama (phi3) + Streamlit")