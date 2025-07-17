from schemas import MoodUpdateRequest
from fastapi import HTTPException
from db import get_supabase
supabase = get_supabase()


def submit_mood_logic(mood: MoodUpdateRequest, supabase):
    result = supabase.table("profiles").update({"mood": mood.mood}).eq("id", mood.user_id).execute()
    if result.get("error"):
        raise HTTPException(status_code=400, detail="Something went wrong")
    return {"message": f"Mood '{mood.mood}' recorded."}


