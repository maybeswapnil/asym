"""
MongoDB Document Models for the MCQ Quiz Platform using Beanie ODM.
"""

from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum

from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING, TEXT

from . import BaseDocument


class DifficultyLevel(str, Enum):
    """Quiz difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(str, Enum):
    """Question types."""
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"


class SessionStatus(str, Enum):
    """Quiz session status."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Quiz(BaseDocument):
    """Quiz document model."""
    
    title: str = Field(..., max_length=200, description="Quiz title")
    description: Optional[str] = Field(None, description="Quiz description")
    category: Optional[str] = Field(None, max_length=100, description="Quiz category")
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="Difficulty level")
    is_active: bool = Field(default=True, description="Whether quiz is active")
    time_limit_minutes: Optional[int] = Field(None, gt=0, description="Time limit in minutes")
    passing_score: Optional[int] = Field(None, ge=0, le=100, description="Passing score percentage")
    total_questions: int = Field(default=0, ge=0, description="Total number of questions")
    
    # Virtual field for questions (populated when needed)
    questions: Optional[List["Question"]] = Field(default=None, exclude=True)
    
    class Settings:
        name = "quizzes"
        indexes = [
            IndexModel([("title", TEXT)]),
            IndexModel([("category", ASCENDING)]),
            IndexModel([("difficulty_level", ASCENDING)]),
            IndexModel([("is_active", ASCENDING)]),
            IndexModel([("created_at", ASCENDING)]),
        ]


class Question(BaseDocument):
    """Question document model."""
    
    quiz_id: str = Field(..., description="Associated quiz ID")
    question_text: str = Field(..., description="Question text")
    question_type: QuestionType = Field(default=QuestionType.SINGLE_CHOICE, description="Question type")
    options: List[str] = Field(..., min_items=2, description="Answer options")
    correct_answers: List[str] = Field(..., min_items=1, description="Correct answer options")
    explanation: Optional[str] = Field(None, description="Answer explanation")
    points: int = Field(default=1, gt=0, description="Points for correct answer")
    order_index: int = Field(default=0, ge=0, description="Question order in quiz")
    is_active: bool = Field(default=True, description="Whether question is active")
    
    class Settings:
        name = "questions"
        indexes = [
            IndexModel([("quiz_id", ASCENDING)]),
            IndexModel([("quiz_id", ASCENDING), ("order_index", ASCENDING)]),
            IndexModel([("is_active", ASCENDING)]),
            IndexModel([("created_at", ASCENDING)]),
        ]


class Answer(BaseDocument):
    """Answer document model."""
    
    user_id: str = Field(..., description="User who submitted the answer")
    quiz_id: str = Field(..., description="Associated quiz ID")
    question_id: str = Field(..., description="Associated question ID")
    selected_answers: List[str] = Field(..., min_items=1, description="Selected answer options")
    is_correct: bool = Field(..., description="Whether answer is correct")
    points_earned: int = Field(default=0, ge=0, description="Points earned")
    time_taken_seconds: Optional[int] = Field(None, ge=0, description="Time taken to answer")
    session_id: Optional[str] = Field(None, description="Associated quiz session ID")
    
    class Settings:
        name = "answers"
        indexes = [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("quiz_id", ASCENDING)]),
            IndexModel([("question_id", ASCENDING)]),
            IndexModel([("session_id", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("quiz_id", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("question_id", ASCENDING)], unique=True),
            IndexModel([("created_at", ASCENDING)]),
        ]


class QuizSession(BaseDocument):
    """Quiz session document model."""
    
    user_id: str = Field(..., description="User taking the quiz")
    quiz_id: str = Field(..., description="Associated quiz ID")
    status: SessionStatus = Field(default=SessionStatus.IN_PROGRESS, description="Session status")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Session start time")
    completed_at: Optional[datetime] = Field(None, description="Session completion time")
    time_limit_minutes: Optional[int] = Field(None, gt=0, description="Time limit for session")
    time_taken_minutes: Optional[int] = Field(None, ge=0, description="Actual time taken")
    
    # Progress tracking
    total_questions: int = Field(default=0, ge=0, description="Total questions in quiz")
    questions_answered: int = Field(default=0, ge=0, description="Questions answered")
    correct_answers: int = Field(default=0, ge=0, description="Correct answers count")
    total_score: int = Field(default=0, ge=0, description="Total points earned")
    max_possible_score: int = Field(default=0, ge=0, description="Maximum possible score")
    percentage_score: Optional[float] = Field(None, ge=0, le=100, description="Percentage score")
    is_passed: Optional[bool] = Field(None, description="Whether quiz was passed")
    
    class Settings:
        name = "quiz_sessions"
        indexes = [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("quiz_id", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("quiz_id", ASCENDING)]),
            IndexModel([("quiz_id", ASCENDING), ("percentage_score", ASCENDING)]),
            IndexModel([("started_at", ASCENDING)]),
            IndexModel([("completed_at", ASCENDING)]),
        ]


# Export all models
__all__ = [
    "Quiz",
    "Question", 
    "Answer",
    "QuizSession",
    "DifficultyLevel",
    "QuestionType", 
    "SessionStatus"
]
