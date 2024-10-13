from fastapi import FastAPI, Request
from pydantic import BaseModel
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
from datetime import datetime

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

# Initialize Anthropic client
client = Anthropic(api_key=api_key)

# Database connection setup
DATABASE_URL = os.getenv("DATABASE_URL")
conn = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request schema
class QuestionRequest(BaseModel):
    question: str

# Default response for non-tax-related questions
DEFAULT_RESPONSE = "Please ask a question related to tax or financial matters."

# Connect to the database on startup
@app.on_event("startup")
async def startup():
    global conn
    conn = await asyncpg.connect(DATABASE_URL)

# Close the database connection on shutdown
@app.on_event("shutdown")
async def shutdown():
    await conn.close()


    # Function to get the past k messages as context
async def get_context_window(user_id: str, session_id: str, k: int = 3):
    query = """
        SELECT prompt, response
        FROM chat_history
        WHERE user_id = $1 AND session_id = $2
        ORDER BY timestamp DESC
        LIMIT $3
    """
    rows = await conn.fetch(query, user_id, session_id, k)
    
    # Reverse the list to maintain the correct order (oldest to newest)
    context = []
    for row in reversed(rows):
        context.append({"role": "user", "content": [{"type": "text", "text": row["prompt"]}]})
        context.append({"role": "assistant", "content": [{"type": "text", "text": row["response"]}]})
    
    return context


# Define the function to get the response from Anthropic
async def get_gpt_response(question, context):
    try:
        context.append({"role": "user", "content": [{"type": "text", "text": question}]})
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0,
            system="You are a highly skilled Tax Filing Assistant .Strictly Dont answer any non tax related question!! Your only goal is to help the user with tax-related questions and calculations, providing clear and accurate information. Please restrict your answer to max 30 words",
            messages=context
        )
        # Extract the text content from TextBlock objects
        return response.content[0].text if isinstance(response.content, list) and response.content else "No answer provided."
    except Exception as e:
        print(f"Error communicating with Anthropic API: {e}")
        return "There was an error generating the response. Please try again later."

# Define the API endpoint
@app.post("/api/tax-question")
async def ask_tax_question(request: Request):
    data = await request.json()
    question = data.get("question", "").lower()

    
    user_id = "charan"
    session_id = "session_1"  
    context = await get_context_window(user_id, session_id, k=3)
    response_text = await get_gpt_response(data["question"], context)

    # Save question and response to the database
    timestamp = datetime.now()
    session_id = "session_1"  # Example session ID, can be customized

    try:
        await conn.execute(
            """
            INSERT INTO chat_history (user_id, prompt, response, timestamp, session_id)
            VALUES ($1, $2, $3, $4, $5)
            """,
            "charan",  # Example user_id, customize if needed
            data["question"],
            response_text,
            timestamp,
            session_id
        )
    except Exception as db_error:
        print(f"Database error: {db_error}")

    # Return the response text to the frontend
    return {"answer": response_text}
