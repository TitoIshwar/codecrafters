from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date



# ------------------- 🔐 Authentication -------------------

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserSignupRequest(BaseModel):
    name: str
    email: str
    password: str

class AuthResponse(BaseModel):
    user_id: str
    token: str
    message: str

# ------------------- 👤 User Profile -------------------
class UserCreateRequest(BaseModel):
    name: str
    username: str
    password: str
    age: Optional[int]
    gender: Optional[str]


class UserUpdateRequest(BaseModel):
    user_id: str
    goal: Optional[str]
    mood: Optional[str]
    freeze_days: Optional[int]
    streak: Optional[int]
    points: Optional[int]

class UserResponse(BaseModel):
    user_id: str
    name: str
    age: Optional[int]
    gender: Optional[str]
    goal: Optional[str]
    streak: int
    freeze_days: int
    points: int
    
class UserStatsResponse(BaseModel):
    streak: int
    points: int   


    
# ------------------- 🎯 Goal Discovery -------------------

class GoalDiscoveryRequest(BaseModel):
    user_id: str

class GoalDiscoveryResponse(BaseModel):
    questions: List[str]
    suggested_goal: Optional[str]
    
class SetUserGoalRequest(BaseModel):
    user_id: str
    goal: str
  

 
  
  


# ------------------- 🧠 Task Personalization -------------------

class TaskPersonalizationRequest(BaseModel):
    user_id: str
    user_goal: str

class TaskPersonalizationResponse(BaseModel):
    root_cause: Optional[str]
    personalized_questions: List[str]

# ------------------- 📅 Daily Task -------------------

class DailyTaskRequest(BaseModel):
    user_id: str
    user_goal: str
    mood: str
    summary_context: str
    progress_summary: str
    is_first_day: bool = False

class DailyTaskResponse(BaseModel):
    task: str
    difficulty: str
    explanation: str
    ask_confirmation: bool

# ------------------- 📈 Feedback & Reflection -------------------

class SelfReflectionRequest(BaseModel):
    user_id: str
    task_id: str
    task_completed: bool
    reflection_text: str

class WeeklyFeedbackRequest(BaseModel):
    user_id: str
    goal: str
    progress_summary: str
    status_summary: str
    mood: str
    improvement_rating: int  # 1-5 scale
    comment: Optional[str] = None

class TaskFeedbackRequest(BaseModel):
    user_id: str
    task_id: str
    rating: int  # 1-5 scale
    feedback: str

class WeeklyFeedbackAIResponse(BaseModel):
    feedback_message: str

# ------------------- 🔄 Task Confirmation and Completion -------------------

class TaskCompleteRequest(BaseModel):
    user_id: str
    task_id: str
    completed: bool
    reason_if_no: Optional[str] = None

# ------------------- 🧘 Mood Tracking -------------------

class MoodUpdateRequest(BaseModel):
    user_id: str
    mood: str

# ------------------- 💬 Quote Generator -------------------

class QuoteRequest(BaseModel):
    theme: Optional[str]  # "motivation", "calm", "growth", etc.

class QuoteResponse(BaseModel):
    quote: str
    author: Optional[str]

# ------------------- 🧠 LLM Context Summary (for RAG / logs) -------------------

class LLMContextSummary(BaseModel):
    user_id: str
    summary_text: str
    date_generated: Optional[date] = Field(default_factory=date.today)

class TaskInfo(BaseModel):
    task_id: str
    date: date
    task_description: str
    task_level: Optional[str] = None
    completed: bool
    feedback: Optional[str] = None
    reflection: Optional[str] = None
    #completion_date: Optional[date] = None

class SummaryRequest(BaseModel):
    user_id: str
    user_goal: str
    recent_tasks: List[str]
    recent_feedback: List[str]
    current_streak: int
    last_week_feedback: Optional[str] = None

class TaskRecapRequest(BaseModel):
    user_id: str
    task_id: str
    response: str