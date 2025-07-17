from datetime import datetime, timedelta
from fastapi import HTTPException
from db import get_supabase

supabase = get_supabase()

async def update_streak_logic(user_id: str, task_completed: bool, used_freeze: bool, supabase):
    profile_result = await supabase.table("profiles").select("streak, freeze_days, last_streak_update").eq("id", user_id).execute()
    if profile_result.get("error") or not profile_result.data:
        raise HTTPException(status_code=404, detail="User not found")

    user = profile_result.data[0]
    current_streak = user.get("streak", 0)
    freeze_days = user.get("freeze_days", 3)
    last_updated_str = user.get("last_streak_update")
    today = datetime.utcnow().date()

    if last_updated_str:
        last_date = datetime.strptime(last_updated_str, "%Y-%m-%d").date()
        if last_date == today:
            return {
                "message": "Streak already updated today.",
                "streak": current_streak,
                "freeze_days": freeze_days
            }

    new_streak = current_streak
    message = ""

    if task_completed:
        new_streak += 1
        message = "✅ Task completed — streak increased."
    elif used_freeze:
        freeze_days -= 1
        message = "🧊 Freeze day used — streak preserved."
    else:
        new_streak = 0
        message = "❌ Task not done — streak reset to 0."

    update_data = {
        "streak": new_streak,
        "last_streak_update": str(today)
    }

    if used_freeze:
        update_data["freeze_days"] = freeze_days

    update_result = await supabase.table("profiles").update(update_data).eq("id", user_id).execute()

    if update_result.get("error"):
        raise HTTPException(status_code=500, detail=f"Failed to update streak/freeze days: {update_result['error']['message']}")

    return {
        "message": message,
        "streak": new_streak,
        "freeze_days": freeze_days
    }


async def perform_daily_streak_check(user_id: str, supabase):
    profile_result = await supabase.table("profiles").select("streak, freeze_days, last_streak_update").eq("id", user_id).execute()
    if profile_result.get("error") or not profile_result.data:
        raise HTTPException(status_code=404, detail="User not found")

    user = profile_result.data[0]
    current_streak = user.get("streak", 0)
    freeze_days = user.get("freeze_days", 0)
    last_updated_str = user.get("last_streak_update")
    today = datetime.utcnow().date()

    if not last_updated_str:
        return {"message": "No last streak record — nothing to reset/check yet."}

    last_date = datetime.strptime(last_updated_str, "%Y-%m-%d").date()

    if (today - last_date).days >= 1:
        if (today - last_date).days == 1:
            if freeze_days > 0:
                result = await update_streak_logic(user_id, task_completed=False, used_freeze=True, supabase=supabase)
                return {"message": f"⏰ Day skipped, but {result['message']}"}
            else:
                result = await update_streak_logic(user_id, task_completed=False, used_freeze=False, supabase=supabase)
                return {"message": f"⏰ Day skipped, {result['message']}"}
        elif (today - last_date).days > 1:
            result = await update_streak_logic(user_id, task_completed=False, used_freeze=False, supabase=supabase)
            return {"message": f"⏰ Multiple days skipped, {result['message']}"}

    return {"message": "✅ Streak still valid or already updated today."}


async def refresh_freeze_days(user_id: str, supabase):
    profile_result = await supabase.table("profiles").select("freeze_days").eq("id", user_id).execute()
    if profile_result.get("error") or not profile_result.data:
        raise HTTPException(status_code=404, detail="User not found")

    freeze_days = profile_result.data[0].get("freeze_days", 0)
    if freeze_days < 3:
        update_result = await supabase.table("profiles").update({"freeze_days": 3}).eq("id", user_id).execute()
        if update_result.get("error"):
            raise HTTPException(status_code=500, detail=f"Failed to refresh freeze days: {update_result['error']['message']}")
        return {"message": "Freeze days refreshed to 3."}

    return {"message": "No refresh needed for freeze days."}


async def use_freeze_logic(user_id: str, supabase):
    profile_result = await supabase.table("profiles").select("freeze_days").eq("id", user_id).execute()
    if profile_result.get("error") or not profile_result.data:
        raise HTTPException(status_code=404, detail="User not found")

    freeze_days = profile_result.data[0].get("freeze_days", 0)

    if freeze_days <= 0:
        streak_reset_result = await update_streak_logic(user_id, task_completed=False, used_freeze=False, supabase=supabase)
        raise HTTPException(
            status_code=400,
            detail=f"All your freeze days are used up. {streak_reset_result['message']}"
        )
    else:
        result = await update_streak_logic(user_id, task_completed=False, used_freeze=True, supabase=supabase)
        refresh_status = await refresh_freeze_days(user_id, supabase)

        return {
            "message": result["message"],
            "streak": result["streak"],
            "freeze_days": result["freeze_days"],
            "refresh_status": refresh_status["message"]
        }