from fastapi import FastAPI, Request
from pydantic import BaseModel
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

# Initialize Anthropic client
client = Anthropic(api_key=api_key)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request schema
class QuestionRequest(BaseModel):
    question: str

# Default response for non-tax-related questions
DEFAULT_RESPONSE = "Please ask a question related to tax or financial matters."

# Define the function to get the response from Anthropic
async def get_gpt_response(question):
    try:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0,
            system="You are a highly skilled Tax Filing Assistant. Your primary goal is to help the user with tax-related questions and calculations, providing clear and accurate information.\n- If the user provides irrelevant or off-topic input (i.e., anything unrelated to taxes or financial matters), politely remind them to focus on tax-related topics. In this case Always make sure you respond within 100 characters.\n- If the user asks for tax advice or calculations, guide them through the necessary details (e.g., income, filing status, deductions, tax credits) and give estimates where appropriate.\n- Always offer to clarify or provide more information when needed, and ensure the user feels informed and supported in their tax filing process.\n- Keep responses concise, but detailed enough to address the user's tax concerns comprehensively.\n- If a user repeatedly asks off-topic questions, kindly but firmly request that they stay on tax topics to get the best assistance. Always make sure you respond within 100 characters.\n\nYour purpose is to streamline tax-related queries, helping the user understand and resolve tax filing, deductions, credits, and any other relevant financial questions.\n",
            messages=[{"role": "user", "content": [{"type": "text", "text": question}]}]
        )
        return response.content
    except Exception as e:
        print(f"Error communicating with Anthropic API: {e}")
        return [{"text": "There was an error generating the response. Please try again later."}]

# Define the API endpoint
@app.post("/api/tax-question")
async def ask_tax_question(request: Request):
    data = await request.json()
    question = data.get("question", "").lower()

    # Check if question is tax-related
    if "tax" not in question:
        return {"answer": [{"text": DEFAULT_RESPONSE}]}

    # Get response from GPT if tax-related
    answer = await get_gpt_response(data["question"])
    return {"answer": answer}
