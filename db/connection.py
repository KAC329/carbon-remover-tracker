"""
db/connection.py
Centralized database connection using SQLAlchemy.
Reads from Streamlit secrets when deployed, .env when local.
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    try:
        import streamlit as st
        host     = st.secrets["DB_HOST"]
        port     = st.secrets["DB_PORT"]
        name     = st.secrets["DB_NAME"]
        user     = st.secrets["DB_USER"]
        password = st.secrets["DB_PASSWORD"]
    except Exception:
        host     = os.getenv("DB_HOST", "localhost")
        port     = os.getenv("DB_PORT", "5432")
        name     = os.getenv("DB_NAME", "carbon_removal_db")
        user     = os.getenv("DB_USER", "carbon_user")
        password = os.getenv("DB_PASSWORD", "carbon_pass")

  url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
  return create_engine(url, pool_pre_ping=True, connect_args={"sslmode": "require"})