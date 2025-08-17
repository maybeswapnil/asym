"""
Pydantic schemas for MCQ Quiz Platform API.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


# Quiz Schemas
class QuizBase(BaseSchema):
    """Base quiz schema."""
    
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    difficulty_level: str = Field("medium", pattern="^(easy|medium|hard)$")
    time_limit_minutes: Optional[int] = Field(None, gt=0)
    passing_score: Optional[int] = Field(None, ge=0, le=100)


class QuizCreate(QuizBase):
    """Schema for creating a quiz."""
    
    is_active: bool = Field(True)


class QuizUpdate(BaseSchema):
    """Schema for updating a quiz."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    difficulty_level: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    time_limit_minutes: Optional[int] = Field(None, gt=0)
    passing_score: Optional[int] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class QuizResponse(QuizBase):
    """Schema for quiz response."""
    
    id: str
    is_active: bool
    total_questions: int
    created_at: datetime
    updated_at: Optional[datetime]


class QuizListResponse(BaseSchema):
    """Schema for quiz list response."""
    
    quizzes: List[QuizResponse]
    total: int
    skip: int
    limit: int


# Question Schemas
class QuestionBase(BaseSchema):
    """Base question schema."""
    
    question_text: str = Field(..., min_length=1)
    question_type: str = Field("single_choice", pattern="^(single_choice|multiple_choice)$")
    difficulty_level: str = Field("medium", pattern="^(easy|medium|hard)$")
    points: int = Field(1, ge=1)
    explanation: Optional[str] = None
    options: List[str] = Field(..., min_items=2, description="List of answer options")
    correct_answers: List[str] = Field(..., min_items=1, description="List of correct answer texts")
    order_index: int = Field(0, ge=0)
    subject: Optional[str] = Field(None, description="Subject/section classification")


class QuestionCreate(QuestionBase):
    """Schema for creating a question."""
    
    quiz_id: str
    is_active: bool = Field(True)


class QuestionUpdate(BaseSchema):
    """Schema for updating a question."""
    
    question_text: Optional[str] = Field(None, min_length=1)
    question_type: Optional[str] = Field(None, pattern="^(single_choice|multiple_choice)$")
    difficulty_level: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    points: Optional[int] = Field(None, ge=1)
    explanation: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answers: Optional[List[str]] = None
    order_index: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class QuestionResponse(QuestionBase):
    """Schema for question response."""
    
    id: str
    quiz_id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]


class QuestionResponsePublic(BaseSchema):
    """Schema for public question response (without correct answers)."""
    
    id: str
    quiz_id: str
    question_text: str
    question_type: str
    difficulty_level: str
    points: int
    options: List[str]
    order_index: int
    subject: Optional[str] = None
    created_at: datetime


# Answer Schemas
class AnswerSubmit(BaseSchema):
    """Schema for submitting an answer."""
    
    question_id: str
    selected_answers: List[str] = Field(..., min_items=1, description="List of selected answer texts")
    session_id: Optional[str] = None
    time_taken_seconds: Optional[int] = Field(None, ge=0)


class AnswerResponse(BaseSchema):
    """Schema for answer response."""
    
    id: str
    user_id: str
    quiz_id: str
    question_id: str
    selected_answers: List[str]
    is_correct: bool
    points_earned: int
    time_taken_seconds: Optional[int]
    session_id: Optional[str]
    created_at: datetime


# Quiz Session Schemas
class QuizSessionStart(BaseSchema):
    """Schema for starting a quiz session."""
    
    quiz_id: str


class QuizSessionResponse(BaseSchema):
    """Schema for quiz session response."""
    
    id: str
    user_id: str
    quiz_id: str
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_score: int
    max_possible_score: int
    percentage_score: Optional[float]
    questions_answered: int
    correct_answers: int
    time_taken_minutes: Optional[int]
    is_passed: Optional[bool]
    created_at: datetime


class LeaderboardEntry(BaseSchema):
    """Schema for leaderboard entry."""
    
    user_id: str
    total_score: int
    percentage_score: Optional[float]
    time_taken_minutes: Optional[int]
    completed_at: Optional[datetime]


# Statistics Schemas
class QuizStatistics(BaseSchema):
    """Schema for quiz statistics."""
    
    quiz_id: str
    total_attempts: int
    average_score: float
    correct_answers: int
    total_answers: int
    accuracy_percentage: float


# Generic Response Schemas
class MessageResponse(BaseSchema):
    """Schema for simple message responses."""
    
    message: str
    success: bool = True


class ErrorResponse(BaseSchema):
    """Schema for error responses."""
    
    detail: str
    error_code: Optional[str] = None
    success: bool = False


# Health Check Schema
class HealthResponse(BaseSchema):
    """Schema for health check response."""
    
    status: str
    service: str = "MCQ Quiz Platform"
    version: str
    timestamp: datetime


# Bulk Operations Schemas
class BulkQuestionCreate(BaseSchema):
    """Schema for bulk question creation."""
    
    quiz_id: str
    questions: List[QuestionBase]


class BulkOperationResponse(BaseSchema):
    """Schema for bulk operation response."""
    
    success_count: int
    failed_count: int
    total_count: int
    errors: Optional[List[str]] = None
