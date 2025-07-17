from schemas import UserStatsResponse, SetUserGoalRequest, GoalDiscoveryRequest, UserCreateRequest, UserLoginRequest, AuthResponse, TaskPersonalizationRequest
from datetime import datetime
from passlib.hash import bcrypt
from uuid import uuid4
from db import get_supabase
from fastapi import HTTPException
from LLM_services import goal_discovery_prompt, Task_personalisation

supabase = get_supabase()

def register_user_logic(user: UserCreateRequest):
    user_id = str(uuid4())
    
    # Hash the password before storing
    hashed_password = bcrypt.hash(user.password)
    
    result = supabase.table("profiles").insert({
        "id": user_id,
        "name": user.name,
        "username": user.username,
        "password": hashed_password,  # Now properly hashed
        "age": user.age,
        "gender": user.gender,
        "streak": 0,
        "points": 0,
        "freeze_days": 3,
        "goal": None
    }).execute()

    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"]["message"])

    return {"message": f"Welcome, {user.name}! Profile created.", "user_id": user_id}

def login_logic(data: UserLoginRequest) -> AuthResponse:
    # Get user from database
    result = supabase.table("profiles").select("*").eq("email", data.email).execute()
    
    if not result.data:
        return {"error": "User not found"}
    
    user = result.data[0]
    
    # Verify password
    if not bcrypt.verify(data.password, user["password"]):
        return {"error": "Invalid password"}
    
    # Generate a token (in a real app, use JWT or similar)
    token = str(uuid4())  # Placeholder token generation
    
    return AuthResponse(
        user_id=user["id"],
        token=token,
        message=f"Welcome back, {user['name']}!"
    )

def update_goal_logic(data: SetUserGoalRequest):
    result = supabase.table("profiles").update({"goal": data.goal}).eq("id", data.user_id).execute()

    if result.get("error"):
        raise HTTPException(status_code=400, detail="Something went wrong")

    return {"message": f"Goal '{data.goal}' set!"}

def get_stats_logic(user_id: str) -> UserStatsResponse:
    result = supabase.table("profiles").select("streak, points").eq("id", user_id).execute()

    if result.get("error"):
        raise HTTPException(status_code=400, detail="Something went wrong")

    data = result["data"][0] if result["data"] else {}
    
    return UserStatsResponse(
        streak=data.get("streak", 0),
        points=data.get("points", 0)
    )

def goal_discovery_logic(data: GoalDiscoveryRequest):
    # Get LLM response for goal discovery
    from LLM_services import goal_discovery_prompt
    messages = goal_discovery_prompt()
    
    # Store the interaction in the database
    result = supabase.table("goal_discovery_sessions").insert({
        "user_id": data.user_id,
        "current_step": "initial",
        "responses": data.responses if hasattr(data, 'responses') else [],
        "date_started": datetime.utcnow().isoformat()
    }).execute()
    
    if result.get("error"):
        raise HTTPException(status_code=400, detail="Something went wrong")
        
    return {"messages": messages, "session_id": result.data[0]["id"]}

def goal_personalization_logic(data: TaskPersonalizationRequest):
    # Get user's current goal
    user_result = supabase.table("profiles").select("goal").eq("id", data.user_id).execute()
    if user_result.get("error") or not user_result.data:
        return {"error": "User not found"}
    
    current_goal = user_result.data[0].get("current_goal")
    if not current_goal:
        raise HTTPException(status_code=400, detail="Something went wrong")
    
    # Get LLM response for task personalization
    from LLM_services import Task_personalisation
    messages = Task_personalisation(current_goal)
    
    # Store personalization session
    session_result = supabase.table("goal_personalization_sessions").insert({
        "user_id": data.user_id,
        "goal": current_goal,
        "responses": data.responses if hasattr(data, 'responses') else [],
        "date_started": datetime.utcnow().isoformat()
    }).execute()
    
    if session_result.get("error"):
        raise HTTPException(status_code=400, detail="Something went wrong")
        
    return {"messages": messages, "session_id": session_result.data[0]["id"]}
