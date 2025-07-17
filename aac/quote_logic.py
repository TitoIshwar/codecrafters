from LLM_services import call_llm
from datetime import datetime
#from fastapi import HTTPException
#from schemas import DailyQuoteResponse
from db import get_supabase
supabase = get_supabase()

def generate_daily_quote():
    today = datetime.utcnow().strftime("%Y-%m-%d")

    messages = [
        {
            "role": "system",
            "content": f"Today is {today}. Generate a short quote under 20 words about motivation, confidence, or growth with a fictional author."
        },
        {
            "role": "user",
            "content": "Please give me today's motivational quote."
        }
    ]

    response = call_llm(messages)
    return parse_quote_response(response)

def parse_quote_response(text: str):
    if " - " in text:
        parts = text.split(" - ")
        return {"quote": parts[0].strip().strip('"'), "author": parts[1].strip()}
    else:
        return {"quote": text.strip(), "author": "Anonymous"}

