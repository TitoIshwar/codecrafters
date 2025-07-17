# routes/core_routes.py

from fastapi import APIRouter
from typing import List
from datetime import datetime, date
from schemas import *
from LLM_services import *
from db import get_supabase
from quote_logic import generate_daily_quote
from feedback_logic import *
#from auth import get_current_user
from freeze_logic import *
from user_logic import register_user_logic, login_logic, update_goal_logic, get_stats_logic, goal_personalization_logic, goal_discovery_logic
from task_logic import (
    get_all_tasks_logic, get_incomplete_tasks_logic, get_completed_tasks_logic,
    generate_task_logic, complete_task_logic, task_recap_logic, task_feedback_logic
)

router = APIRouter()
supabase = get_supabase()

# -------------------- 1. Register User --------------------
@router.post("/register")
def register_user(data: UserCreateRequest):
    return register_user_logic(data, supabase)

# -------------------- 2. Login --------------------
@router.post("/login")
def login_user(data: UserLoginRequest):
    return login_logic(data)

# -------------------- 3. Mood Submission --------------------
@router.post("/mood")
def submit_mood(data: MoodUpdateRequest):
    from mood_input import submit_mood_logic
    return submit_mood_logic(data, supabase)

# -------------------- 4. Goal Discovery --------------------
@router.post("/goal/discovery")
def goal_discovery(data: GoalDiscoveryRequest):
    return goal_discovery_logic(data)

# -------------------- 5. Set Goal --------------------
@router.post("/goal/set")
def set_goal(data: SetUserGoalRequest):
    return update_goal_logic(data)

# -------------------- 6. Personalize Goal --------------------
@router.post("/goal/personalise")
def personalize_goal(data: TaskPersonalizationRequest):
    return goal_personalization_logic(data, supabase)

# -------------------- 7. Daily Task --------------------
@router.post("/task/daily")
def get_daily_task(data: DailyTaskRequest):
    return generate_task_logic(data, supabase)

# -------------------- 8. Complete Task --------------------
@router.post("/task/complete")
def complete_task(data: TaskCompleteRequest):
    return complete_task_logic(data, supabase)

# -------------------- 9. Self Reflection --------------------
@router.post("/task/self-reflection")
def task_self_reflection(data: SelfReflectionRequest):
    return task_self_reflection_logic(data)

# -------------------- 10. Weekly Feedback --------------------
@router.post("/feedback/weekly")
def weekly_feedback(data: WeeklyFeedbackRequest) -> WeeklyFeedbackAIResponse:
    return weekly_feedback_logic(data, supabase)

@router.get("/feedback/progress")
def get_progress(user_id: str):
    return progress_report_logic(user_id)   

# -------------------- 11. Task Management --------------------
@router.get("/tasks/all", response_model=List[TaskInfo])
def get_all_tasks(user_id: str):
    return get_all_tasks_logic(user_id, supabase)

@router.get("/tasks/incomplete", response_model=List[TaskInfo])
def get_incomplete(user_id: str):
    return get_incomplete_tasks_logic(user_id, supabase)

@router.get("/tasks/completed", response_model=List[TaskInfo])
def get_completed(user_id: str):
    return get_completed_tasks_logic(user_id, supabase)

# -------------------- 12. Profile Stats --------------------
@router.get("/profile/stats", response_model=UserStatsResponse)
def get_stats(user_id: str):
    return get_stats_logic(user_id)

# -------------------- 13. Quote of the Day --------------------
@router.get("/quote", response_model=QuoteResponse)
def get_quote():
    return generate_daily_quote()

# -------------------- 14. Task Feedback & Recap --------------------
@router.post("/task/feedback")
def task_feedback(data: TaskFeedbackRequest):
    return task_feedback_logic(data, supabase)

@router.post("/task/recap")
def get_task_recap(user_id: str):
    return task_recap_logic(user_id, supabase)

# -------------------- 15. Freeze Day --------------------
@router.post("/freeze")
def use_freeze(user_id: str):
    return use_freeze_logic(user_id, supabase)

@router.get("/test-db")
def test_db():
    try:
        result = supabase.table("profiles").select("*").limit(1).execute()
        return {"success": True, "data": result["data"]}
    except Exception as e:
        return {"success": False, "error": str(e)}
