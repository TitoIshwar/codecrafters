from schemas import WeeklyFeedbackRequest, LLMContextSummary, WeeklyFeedbackAIResponse
from LLM_services import weekly_feedback_prompt
from datetime import date
from fastapi import HTTPException
from db import get_supabase

supabase = get_supabase()



def weekly_feedback_logic(data: WeeklyFeedbackRequest, supabase) -> WeeklyFeedbackAIResponse:
    result = supabase.table("weekly_feedback").insert({
        "user_id": data.user_id,
        "improvement_rating": data.improvement_rating,
        "comment": data.comment,
        "week_start": date.today().isoformat()
    }).execute()

    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"]["message"])

    messages = weekly_feedback_prompt(
        data.goal,
        data.progress_summary,
        data.status_summary,
        data.mood
    )
    return WeeklyFeedbackAIResponse(feedback_message=messages)

def progress_report_logic(user_id: str, supabase):
    result = supabase.table("weekly_feedback").select("*").eq("user_id", user_id).order("week_start", desc=True).limit(4).execute()

    if result.get("error"):
        raise HTTPException(status_code=400, detail="Failed to fetch feedback")

    feedbacks = result.data
    if not feedbacks:
        return {"report": "No progress data available yet."}

    avg_rating = sum(f["improvement_rating"] for f in feedbacks) / len(feedbacks)
    return {
        "report": f"Your average improvement rating is {avg_rating:.1f}/5 over the past {len(feedbacks)} weeks."
    }

def generate_summary_logic(data: LLMContextSummary, supabase):
    result = supabase.table("weekly_summaries").insert({
        "user_id": data.user_id,
        "summary": data.summary_text,
        "date_generated": data.date_generated.isoformat()
    }).execute()

    if result.get("error"):
        raise HTTPException(status_code=400, detail="Failed to store summary")

    return {"summary": data.summary_text}
