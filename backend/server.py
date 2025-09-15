from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import httpx
import firebase_admin
from firebase_admin import credentials, auth
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize Firebase Admin SDK (Mock for demo)
# For demo purposes, we'll skip Firebase initialization since we're using mock auth
firebase_initialized = False
try:
    firebase_admin.get_app()
    firebase_initialized = True
except ValueError:
    # Skip Firebase initialization for demo - using mock authentication
    logging.info("Skipping Firebase initialization - using mock authentication for demo")

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    firebase_uid: str
    email: str
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    firebase_uid: str
    email: str
    name: str

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectCreate(BaseModel):
    title: str
    description: str = ""

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    title: str
    description: str = ""
    status: str = "backlog"  # backlog, todo, in_progress, done
    position: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    status: str = "backlog"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    position: Optional[int] = None

class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    event_type: str  # study, work, personal
    datetime: datetime
    duration: int = 60  # minutes
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EventCreate(BaseModel):
    title: str
    event_type: str
    datetime: datetime
    duration: int = 60

class Flashcard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    question: str
    answer: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FlashcardCreate(BaseModel):
    question: str
    answer: str

# Firebase Auth Dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # In production, verify the Firebase token here
        # For demo purposes, we'll create a mock user
        token = credentials.credentials
        if not token.startswith('mock_'):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Extract user ID from mock token
        user_id = token.replace('mock_', '')
        user = await db.users.find_one({"firebase_uid": user_id})
        if not user:
            # Create a new user if not exists
            user_data = {
                "id": str(uuid.uuid4()),
                "firebase_uid": user_id,
                "email": f"user{user_id}@example.com",
                "name": f"User {user_id}",
                "created_at": datetime.now(timezone.utc)
            }
            await db.users.insert_one(user_data)
            return User(**user_data)
        return User(**user)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")

# ZenQuotes API
async def get_motivational_quote():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://zenquotes.io/api/today")
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return {"quote": data[0]["q"], "author": data[0]["a"]}
    except Exception as e:
        logging.error(f"Error fetching quote: {e}")
    
    # Fallback quote
    return {"quote": "The way to get started is to quit talking and begin doing.", "author": "Walt Disney"}

# Routes
@api_router.get("/")
async def root():
    return {"message": "Prodigy API is running"}

@api_router.get("/quote")
async def get_quote():
    return await get_motivational_quote()

@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    user_dict = user_data.dict()
    user_obj = User(**user_dict)
    await db.users.insert_one(user_obj.dict())
    return user_obj

@api_router.get("/users/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Projects endpoints
@api_router.post("/projects", response_model=Project)
async def create_project(project_data: ProjectCreate, current_user: User = Depends(get_current_user)):
    project_dict = project_data.dict()
    project_dict["user_id"] = current_user.id
    project_obj = Project(**project_dict)
    await db.projects.insert_one(project_obj.dict())
    return project_obj

@api_router.get("/projects", response_model=List[Project])
async def get_projects(current_user: User = Depends(get_current_user)):
    projects = await db.projects.find({"user_id": current_user.id}).to_list(1000)
    return [Project(**project) for project in projects]

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str, current_user: User = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project)

# Tasks endpoints
@api_router.post("/projects/{project_id}/tasks", response_model=Task)
async def create_task(project_id: str, task_data: TaskCreate, current_user: User = Depends(get_current_user)):
    # Verify project belongs to user
    project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    task_dict = task_data.dict()
    task_dict["project_id"] = project_id
    task_obj = Task(**task_dict)
    await db.tasks.insert_one(task_obj.dict())
    return task_obj

@api_router.get("/projects/{project_id}/tasks", response_model=List[Task])
async def get_tasks(project_id: str, current_user: User = Depends(get_current_user)):
    # Verify project belongs to user
    project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    tasks = await db.tasks.find({"project_id": project_id}).sort("position").to_list(1000)
    return [Task(**task) for task in tasks]

@api_router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate, current_user: User = Depends(get_current_user)):
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify project belongs to user
    project = await db.projects.find_one({"id": task["project_id"], "user_id": current_user.id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = {k: v for k, v in task_update.dict().items() if v is not None}
    await db.tasks.update_one({"id": task_id}, {"$set": update_data})
    
    updated_task = await db.tasks.find_one({"id": task_id})
    return Task(**updated_task)

# Events endpoints
@api_router.post("/events", response_model=Event)
async def create_event(event_data: EventCreate, current_user: User = Depends(get_current_user)):
    event_dict = event_data.dict()
    event_dict["user_id"] = current_user.id
    # Convert datetime to ISO string for MongoDB
    if isinstance(event_dict["datetime"], datetime):
        event_dict["datetime"] = event_dict["datetime"].isoformat()
    event_obj = Event(**event_dict)
    await db.events.insert_one(event_obj.dict())
    return event_obj

@api_router.get("/events", response_model=List[Event])
async def get_events(current_user: User = Depends(get_current_user)):
    events = await db.events.find({"user_id": current_user.id}).to_list(1000)
    for event in events:
        if isinstance(event["datetime"], str):
            event["datetime"] = datetime.fromisoformat(event["datetime"])
    return [Event(**event) for event in events]

@api_router.get("/events/today")
async def get_today_events(current_user: User = Depends(get_current_user)):
    today = datetime.now(timezone.utc).date()
    events = await db.events.find({"user_id": current_user.id}).to_list(1000)
    today_events = []
    for event in events:
        event_datetime = event["datetime"]
        if isinstance(event_datetime, str):
            event_datetime = datetime.fromisoformat(event_datetime)
        if event_datetime.date() == today:
            event["datetime"] = event_datetime
            today_events.append(Event(**event))
    return today_events

# Flashcards endpoints
@api_router.post("/flashcards", response_model=Flashcard)
async def create_flashcard(flashcard_data: FlashcardCreate, current_user: User = Depends(get_current_user)):
    flashcard_dict = flashcard_data.dict()
    flashcard_dict["user_id"] = current_user.id
    flashcard_obj = Flashcard(**flashcard_dict)
    await db.flashcards.insert_one(flashcard_obj.dict())
    return flashcard_obj

@api_router.get("/flashcards", response_model=List[Flashcard])
async def get_flashcards(current_user: User = Depends(get_current_user)):
    flashcards = await db.flashcards.find({"user_id": current_user.id}).to_list(1000)
    return [Flashcard(**flashcard) for flashcard in flashcards]

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()