from schemas import (
    DailyTaskRequest,
    TaskFeedbackRequest,
    TaskInfo,
    TaskRecapRequest,
    TaskCompleteRequest,)
from LLM_services import Daily_task_prompt, self_reflection
from fastapi import HTTPException
from datetime import date



def generate_task_logic(data: DailyTaskRequest, supabase):
    prompt = Daily_task_prompt(
        user_goal=data.user_goal,
        Summary_context=data.summary_context,
        feedback=data.feedback,
        progress_summary=data.progress_summary,
        is_first_day=data.is_first_day
    )

    return {"task_prompt": prompt}


def complete_task_logic(data: TaskCompleteRequest, supabase):
    result = supabase.table("tasks").update({
        "completed": True
    }).eq("user_id", data.user_id).eq("id", data.task_id).execute()

    if result.get("error"):
        raise HTTPException(status_code=400, detail="Failed to mark task complete")

    return {"message": "✅ Task marked as complete"}


def task_feedback_logic(data: TaskFeedbackRequest, supabase):
    result = supabase.table("tasks").update({
        "feedback": data.feedback
    }).eq("user_id", data.user_id).eq("id", data.task_id).execute()

    if result.get("error"):
        raise HTTPException(status_code=400, detail="Failed to save feedback")

    return {"message": "📝 Task feedback saved"}


def task_recap_logic(data: TaskRecapRequest, supabase):
    messages = self_reflection()

    result = supabase.table("task_reflections").insert({
        "user_id": data.user_id,
        "task_id": data.task_id,
        "response": data.response,
        "date": date.today().isoformat()
    }).execute()

    if result.get("error"):
        raise HTTPException(status_code=400, detail="Failed to store reflection")

    return {"messages": messages}


def get_all_tasks_logic(user_id: str, supabase):
    result = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
    if result.get("error"):
        raise HTTPException(status_code=400, detail="Could not fetch tasks")
    return result["data"]


def get_incomplete_tasks_logic(user_id: str, supabase):
    result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("completed", False).execute()
    if result.get("error"):
        raise HTTPException(status_code=400, detail="Could not fetch incomplete tasks")
    return result["data"]


def get_completed_tasks_logic(user_id: str, supabase):
    result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("completed", True).execute()
    if result.get("error"):
        raise HTTPException(status_code=400, detail="Could not fetch completed tasks")
    return result["data"]
