# create_database.py

import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# SQL statement to create the chat_history table
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT
);
"""

async def create_table():
    """Function to connect to the database and create the chat_history table."""
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute(CREATE_TABLE_SQL)
        print("Table chat_history created successfully!")
    finally:
        await conn.close()

# Entry point for running the script
if __name__ == "__main__":
    import asyncio
    asyncio.run(create_table())
