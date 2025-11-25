"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, date
from enum import Enum
import uuid
import os
from pathlib import Path

# Enums for type safety
class EventType(str, Enum):
    FREE = "free"
    PAID = "paid"

class UserRole(str, Enum):
    STUDENT = "student"
    ORGANIZER = "organizer"
    ADMIN = "admin"

class EventStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class PointType(str, Enum):
    REGISTRATION = "registration"
    ATTENDANCE = "attendance"
    COMPLETION = "completion"
    CERTIFICATE = "certificate"
    EARLY_BIRD = "early_bird"
    FIRST_TIME = "first_time"
    STREAK = "streak"
    FEEDBACK = "feedback"

class BadgeType(str, Enum):
    SPORTS = "sports"
    ACADEMIC = "academic"
    ARTS = "arts"
    COMMUNITY = "community"
    MILESTONE_10 = "milestone_10"
    MILESTONE_50 = "milestone_50"
    MILESTONE_100 = "milestone_100"
    PERFECT_MONTH = "perfect_month"
    EARLY_BIRD = "early_bird"

# Pydantic models for API
class PointRecord(BaseModel):
    id: str
    user_email: str
    event_id: str
    points_earned: int
    point_type: PointType
    reason: str
    date_awarded: datetime

class Badge(BaseModel):
    id: str
    badge_type: BadgeType
    name: str
    description: str
    icon_url: Optional[str] = None
    requirements: str

class UserBadge(BaseModel):
    user_email: str
    badge_id: str
    earned_date: datetime
    badge_level: int = 1

class LeaderboardEntry(BaseModel):
    user_email: str
    user_name: str
    total_points: int
    rank: int
    badges_count: int
    recent_activity: str

class Participant(BaseModel):
    email: str
    name: str
    enrollment_date: datetime
    points: int = 0
    certificates: List[str] = []
    whatsapp_group: Optional[str] = None
    badges: List[str] = []

class Event(BaseModel):
    id: str
    name: str
    description: str
    organizer: str
    organizer_email: str
    schedule: str
    event_date: date
    max_participants: int
    event_type: EventType
    fee: float = 0.0
    banner_url: Optional[str] = None
    whatsapp_group: Optional[str] = None
    status: EventStatus = EventStatus.PUBLISHED
    participants: List[Participant] = []
    created_at: datetime
    updated_at: datetime

class User(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    organization: Optional[str] = None
    profile_picture: Optional[str] = None
    created_at: datetime
    points: int = 0

app = FastAPI(title="Mergington High School API",
              description="Enhanced API for comprehensive event management and extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory databases
events: Dict[str, Event] = {}
users: Dict[str, User] = {}
point_records: List[PointRecord] = []
user_badges: List[UserBadge] = []
badges: Dict[str, Badge] = {}

# Points configuration
POINT_VALUES = {
    PointType.REGISTRATION: 5,
    PointType.ATTENDANCE: 10,
    PointType.COMPLETION: 15,
    PointType.CERTIFICATE: 25,
    PointType.EARLY_BIRD: 5,
    PointType.FIRST_TIME: 10,
    PointType.STREAK: 20,
    PointType.FEEDBACK: 3
}

# Initialize sample data
def initialize_sample_data():
    now = datetime.now()
    
    # Initialize badges
    sample_badges = [
        Badge(id="b1", badge_type=BadgeType.SPORTS, name="Sports Enthusiast", 
              description="Participate in 5 sports events", requirements="5 sports events"),
        Badge(id="b2", badge_type=BadgeType.ACADEMIC, name="Academic Star", 
              description="Complete 5 academic events", requirements="5 academic events"),
        Badge(id="b3", badge_type=BadgeType.MILESTONE_10, name="Event Explorer", 
              description="Participate in 10 events", requirements="10 events total"),
        Badge(id="b4", badge_type=BadgeType.EARLY_BIRD, name="Early Bird", 
              description="Register early for 3 events", requirements="3 early registrations"),
        Badge(id="b5", badge_type=BadgeType.PERFECT_MONTH, name="Perfect Month", 
              description="Attend all registered events in a month", requirements="100% attendance in a month")
    ]
    
    for badge in sample_badges:
        badges[badge.id] = badge
    
    # Create sample users with more students
    sample_users = [
        User(id="u1", name="Dr. Smith", email="smith@mergington.edu",
             role=UserRole.ORGANIZER, organization="Chess Club", created_at=now, points=150),
        User(id="u2", name="Prof. Johnson", email="johnson@mergington.edu",
             role=UserRole.ORGANIZER, organization="Programming Department", created_at=now, points=200),
        User(id="u3", name="Michael Chen", email="michael@mergington.edu",
             role=UserRole.STUDENT, created_at=now, points=85),
        User(id="u4", name="Emma Davis", email="emma@mergington.edu",
             role=UserRole.STUDENT, created_at=now, points=120),
        User(id="u5", name="Liam Wilson", email="liam@mergington.edu",
             role=UserRole.STUDENT, created_at=now, points=95),
        User(id="u6", name="Sophia Johnson", email="sophia@mergington.edu",
             role=UserRole.STUDENT, created_at=now, points=110),
        User(id="u7", name="Noah Brown", email="noah@mergington.edu",
             role=UserRole.STUDENT, created_at=now, points=75),
        User(id="u8", name="Daniel Garcia", email="daniel@mergington.edu",
             role=UserRole.STUDENT, created_at=now, points=65)
    ]
    
    for user in sample_users:
        users[user.id] = user
    
    # Create sample events
    sample_events = [
        Event(
            id="e1", name="Chess Club",
            description="Learn strategies and compete in chess tournaments",
            organizer="Dr. Smith", organizer_email="smith@mergington.edu",
            schedule="Fridays, 3:30 PM - 5:00 PM",
            event_date=date(2024, 12, 15),
            max_participants=12, event_type=EventType.FREE,
            participants=[
                Participant(email="michael@mergington.edu", name="Michael", enrollment_date=now, points=10),
                Participant(email="daniel@mergington.edu", name="Daniel", enrollment_date=now, points=15)
            ],
            created_at=now, updated_at=now
        ),
        Event(
            id="e2", name="Programming Class",
            description="Learn programming fundamentals and build software projects",
            organizer="Prof. Johnson", organizer_email="johnson@mergington.edu",
            schedule="Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            event_date=date(2024, 12, 20),
            max_participants=20, event_type=EventType.PAID, fee=50.0,
            participants=[
                Participant(email="emma@mergington.edu", name="Emma", enrollment_date=now, points=25),
                Participant(email="sophia@mergington.edu", name="Sophia", enrollment_date=now, points=20)
            ],
            created_at=now, updated_at=now
        ),
        Event(
            id="e3", name="Soccer Team",
            description="Join the school soccer team and compete in matches",
            organizer="Coach Wilson", organizer_email="wilson@mergington.edu",
            schedule="Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            event_date=date(2024, 12, 18),
            max_participants=22, event_type=EventType.FREE,
            whatsapp_group="https://chat.whatsapp.com/soccer-team",
            participants=[
                Participant(email="liam@mergington.edu", name="Liam", enrollment_date=now, points=30,
                           whatsapp_group="https://chat.whatsapp.com/soccer-team"),
                Participant(email="noah@mergington.edu", name="Noah", enrollment_date=now, points=28)
            ],
            created_at=now, updated_at=now
        )
    ]
    
    for event in sample_events:
        events[event.id] = event

# Initialize sample data on startup
initialize_sample_data()


# Points system functions
def award_points(user_email: str, event_id: str, point_type: PointType, reason: str = "") -> int:
    """Award points to a user and return total points earned"""
    points_earned = POINT_VALUES.get(point_type, 0)
    
    # Create point record
    point_record = PointRecord(
        id=str(uuid.uuid4()),
        user_email=user_email,
        event_id=event_id,
        points_earned=points_earned,
        point_type=point_type,
        reason=reason or f"Points for {point_type.value}",
        date_awarded=datetime.now()
    )
    point_records.append(point_record)
    
    # Update user's total points
    for user in users.values():
        if user.email == user_email:
            user.points += points_earned
            break
    
    # Check for badge eligibility
    check_badge_eligibility(user_email)
    
    return points_earned

def check_badge_eligibility(user_email: str):
    """Check if user is eligible for any new badges"""
    user_points = sum(record.points_earned for record in point_records if record.user_email == user_email)
    user_events = len(set(record.event_id for record in point_records if record.user_email == user_email))
    
    # Check milestone badges
    if user_events >= 10 and not has_badge(user_email, "b3"):
        award_badge(user_email, "b3")
    
    # Check early bird badge
    early_bird_count = len([r for r in point_records if r.user_email == user_email and r.point_type == PointType.EARLY_BIRD])
    if early_bird_count >= 3 and not has_badge(user_email, "b4"):
        award_badge(user_email, "b4")

def has_badge(user_email: str, badge_id: str) -> bool:
    """Check if user has a specific badge"""
    return any(ub.user_email == user_email and ub.badge_id == badge_id for ub in user_badges)

def award_badge(user_email: str, badge_id: str):
    """Award a badge to a user"""
    if not has_badge(user_email, badge_id):
        user_badge = UserBadge(
            user_email=user_email,
            badge_id=badge_id,
            earned_date=datetime.now()
        )
        user_badges.append(user_badge)

def calculate_leaderboard() -> List[LeaderboardEntry]:
    """Calculate and return leaderboard entries"""
    leaderboard = []
    
    for user in users.values():
        if user.role == UserRole.STUDENT:  # Only include students in leaderboard
            user_badge_count = len([ub for ub in user_badges if ub.user_email == user.email])
            recent_records = [r for r in point_records if r.user_email == user.email]
            recent_activity = "No recent activity"
            if recent_records:
                latest_record = max(recent_records, key=lambda x: x.date_awarded)
                recent_activity = f"Earned {latest_record.points_earned} points for {latest_record.reason}"
            
            leaderboard.append(LeaderboardEntry(
                user_email=user.email,
                user_name=user.name,
                total_points=user.points,
                rank=0,  # Will be set after sorting
                badges_count=user_badge_count,
                recent_activity=recent_activity
            ))
    
    # Sort by points (descending) and assign ranks
    leaderboard.sort(key=lambda x: x.total_points, reverse=True)
    for i, entry in enumerate(leaderboard):
        entry.rank = i + 1
    
    return leaderboard

# API Endpoints
@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")

@app.get("/events")
def get_events():
    """Get all published events"""
    return {"events": [event for event in events.values() if event.status == EventStatus.PUBLISHED]}

@app.get("/events/{event_id}")
def get_event(event_id: str):
    """Get a specific event by ID"""
    if event_id not in events:
        raise HTTPException(status_code=404, detail="Event not found")
    return events[event_id]

@app.post("/events/{event_id}/register")
def register_for_event(event_id: str, user_email: str, user_name: str):
    """Register a student for an event with points system"""
    if event_id not in events:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = events[event_id]
    
    # Check if already registered
    if any(p.email == user_email for p in event.participants):
        raise HTTPException(status_code=400, detail="Already registered for this event")
    
    # Check capacity
    if len(event.participants) >= event.max_participants:
        raise HTTPException(status_code=400, detail="Event is full")
    
    # Add participant
    participant = Participant(
        email=user_email,
        name=user_name,
        enrollment_date=datetime.now(),
        points=0
    )
    event.participants.append(participant)
    
    # Award registration points
    points_earned = award_points(user_email, event_id, PointType.REGISTRATION, f"Registered for {event.name}")
    
    # Check for early bird bonus (if event is more than 7 days away)
    days_until_event = (event.event_date - date.today()).days
    if days_until_event > 7:
        bonus_points = award_points(user_email, event_id, PointType.EARLY_BIRD, f"Early bird registration for {event.name}")
        points_earned += bonus_points
    
    return {
        "message": f"Successfully registered for {event.name}",
        "points_earned": points_earned,
        "total_points": sum(record.points_earned for record in point_records if record.user_email == user_email)
    }

@app.delete("/events/{event_id}/unregister")
def unregister_from_event(event_id: str, user_email: str):
    """Unregister from an event"""
    if event_id not in events:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = events[event_id]
    
    # Find and remove participant
    event.participants = [p for p in event.participants if p.email != user_email]
    
    return {"message": f"Unregistered from {event.name}"}

@app.get("/leaderboard")
def get_leaderboard(limit: int = 50):
    """Get the student leaderboard"""
    leaderboard = calculate_leaderboard()
    return {"leaderboard": leaderboard[:limit]}

@app.get("/leaderboard/user/{user_email}")
def get_user_ranking(user_email: str):
    """Get a specific user's ranking and stats"""
    leaderboard = calculate_leaderboard()
    user_entry = next((entry for entry in leaderboard if entry.user_email == user_email), None)
    
    if not user_entry:
        raise HTTPException(status_code=404, detail="User not found in leaderboard")
    
    # Get user's point history
    user_points = [record for record in point_records if record.user_email == user_email]
    user_badge_list = [ub for ub in user_badges if ub.user_email == user_email]
    
    return {
        "ranking": user_entry,
        "point_history": sorted(user_points, key=lambda x: x.date_awarded, reverse=True)[:10],
        "badges": user_badge_list
    }

@app.get("/badges")
def get_all_badges():
    """Get all available badges"""
    return {"badges": list(badges.values())}

@app.get("/user/{user_email}/badges")
def get_user_badges(user_email: str):
    """Get badges earned by a specific user"""
    user_badge_list = [ub for ub in user_badges if ub.user_email == user_email]
    badge_details = []
    
    for user_badge in user_badge_list:
        badge = badges.get(user_badge.badge_id)
        if badge:
            badge_details.append({
                "badge": badge,
                "earned_date": user_badge.earned_date,
                "level": user_badge.badge_level
            })
    
    return {"user_badges": badge_details}

@app.post("/events/{event_id}/mark-attendance")
def mark_attendance(event_id: str, user_email: str):
    """Mark attendance for an event and award points"""
    if event_id not in events:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = events[event_id]
    participant = next((p for p in event.participants if p.email == user_email), None)
    
    if not participant:
        raise HTTPException(status_code=400, detail="User not registered for this event")
    
    # Award attendance points
    points_earned = award_points(user_email, event_id, PointType.ATTENDANCE, f"Attended {event.name}")
    
    return {
        "message": f"Attendance marked for {event.name}",
        "points_earned": points_earned
    }

@app.post("/events/{event_id}/complete")
def complete_event(event_id: str, user_email: str):
    """Mark event as completed and award completion points"""
    if event_id not in events:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = events[event_id]
    participant = next((p for p in event.participants if p.email == user_email), None)
    
    if not participant:
        raise HTTPException(status_code=400, detail="User not registered for this event")
    
    # Award completion points
    points_earned = award_points(user_email, event_id, PointType.COMPLETION, f"Completed {event.name}")
    
    return {
        "message": f"Event completed: {event.name}",
        "points_earned": points_earned
    }
