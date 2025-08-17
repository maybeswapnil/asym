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


class QuizType(str, Enum):
    """Quiz types for different purposes."""
    PRACTICE = "practice"
    MOCK_TEST = "mock_test"
    REAL_EXAM = "real_exam"
    SECTIONAL = "sectional"


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
    quiz_type: QuizType = Field(default=QuizType.PRACTICE, description="Type of quiz")
    is_active: bool = Field(default=True, description="Whether quiz is active")
    time_limit_minutes: Optional[int] = Field(None, gt=0, description="Time limit in minutes")
    passing_score: Optional[int] = Field(None, ge=0, le=100, description="Passing score percentage")
    total_questions: int = Field(default=0, ge=0, description="Total number of questions")
    
    # Exam-specific fields for predictions
    exam_year: Optional[int] = Field(None, description="Year of the exam (e.g., 2024 for CAT 2024)")
    subjects: Optional[List[str]] = Field(default_factory=list, description="List of subjects/sections")
    is_prediction_enabled: bool = Field(default=False, description="Whether to generate predictions for this quiz")
    based_on_exam_id: Optional[str] = Field(None, description="Real exam this mock is based on")
    
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
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="Difficulty level")
    
    # Subject/section classification for predictions
    subject: Optional[str] = Field(None, description="Subject/section this question belongs to")
    topic: Optional[str] = Field(None, description="Specific topic within subject")
    difficulty_weight: float = Field(default=1.0, description="Difficulty weight for prediction models")
    
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
    
    # Subject-wise performance for predictions
    subject_scores: Optional[dict] = Field(default_factory=dict, description="Subject-wise scores {subject: {correct: int, total: int, percentage: float}}")
    
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


class RealExamResult(BaseDocument):
    """Real exam results for building prediction models."""
    
    exam_name: str = Field(..., description="Name of the exam (e.g., CAT 2024)")
    exam_year: int = Field(..., description="Year of the exam")
    user_id: str = Field(..., description="User who took the exam")
    
    # Overall results
    overall_rank: int = Field(..., gt=0, description="Overall rank in exam")
    overall_percentile: float = Field(..., ge=0, le=100, description="Overall percentile")
    total_score: float = Field(..., ge=0, description="Total score obtained")
    max_score: float = Field(..., gt=0, description="Maximum possible score")
    percentage_score: float = Field(..., ge=0, le=100, description="Percentage score")
    
    # Subject-wise results
    subject_percentiles: dict = Field(..., description="Subject-wise percentiles {subject: percentile}")
    subject_scores: dict = Field(..., description="Subject-wise raw scores {subject: score}")
    subject_ranks: Optional[dict] = Field(default_factory=dict, description="Subject-wise ranks {subject: rank}")
    
    # Exam metadata
    total_candidates: int = Field(..., gt=0, description="Total number of candidates")
    cutoff_percentile: Optional[float] = Field(None, description="Cutoff percentile for qualification")
    
    class Settings:
        name = "real_exam_results"
        indexes = [
            IndexModel([("exam_name", ASCENDING)]),
            IndexModel([("exam_year", ASCENDING)]),
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("overall_rank", ASCENDING)]),
            IndexModel([("overall_percentile", ASCENDING)]),
            IndexModel([("exam_name", ASCENDING), ("exam_year", ASCENDING)]),
        ]


class PredictionModel(BaseDocument):
    """Prediction model configurations and parameters."""
    
    model_name: str = Field(..., description="Name of the prediction model")
    exam_name: str = Field(..., description="Target exam (e.g., CAT)")
    model_version: str = Field(..., description="Model version")
    is_active: bool = Field(default=True, description="Whether model is active")
    
    # Model parameters
    training_data_size: int = Field(..., gt=0, description="Size of training dataset")
    accuracy_metrics: dict = Field(..., description="Model accuracy metrics")
    feature_weights: dict = Field(..., description="Feature importance weights")
    
    # Model configuration
    subjects: List[str] = Field(..., description="Subjects this model predicts for")
    min_mock_tests_required: int = Field(default=3, description="Minimum mock tests required for prediction")
    confidence_threshold: float = Field(default=0.7, description="Minimum confidence for predictions")
    
    class Settings:
        name = "prediction_models"
        indexes = [
            IndexModel([("exam_name", ASCENDING)]),
            IndexModel([("model_name", ASCENDING)]),
            IndexModel([("is_active", ASCENDING)]),
        ]


class UserPrediction(BaseDocument):
    """Predicted results for mock test users."""
    
    user_id: str = Field(..., description="User for whom prediction is made")
    quiz_session_id: str = Field(..., description="Mock test session ID")
    target_exam: str = Field(..., description="Target exam (e.g., CAT 2025)")
    prediction_model_id: str = Field(..., description="Model used for prediction")
    
    # Predicted overall results
    predicted_rank: int = Field(..., gt=0, description="Predicted overall rank")
    predicted_percentile: float = Field(..., ge=0, le=100, description="Predicted overall percentile")
    rank_confidence: float = Field(..., ge=0, le=1, description="Confidence in rank prediction")
    percentile_confidence: float = Field(..., ge=0, le=1, description="Confidence in percentile prediction")
    
    # Predicted subject-wise results
    subject_percentiles: dict = Field(..., description="Predicted subject-wise percentiles")
    subject_ranks: dict = Field(default_factory=dict, description="Predicted subject-wise ranks")
    subject_confidence: dict = Field(default_factory=dict, description="Confidence in subject predictions")
    
    # Prediction metadata
    based_on_mock_tests: List[str] = Field(..., description="Mock test session IDs used for prediction")
    prediction_factors: dict = Field(default_factory=dict, description="Factors that influenced prediction")
    improvement_suggestions: List[str] = Field(default_factory=list, description="Areas for improvement")
    
    # Performance trends
    performance_trend: str = Field(default="stable", description="upward/downward/stable trend")
    expected_score_range: dict = Field(default_factory=dict, description="Expected score range {min: float, max: float}")
    
    class Settings:
        name = "user_predictions"
        indexes = [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("target_exam", ASCENDING)]),
            IndexModel([("quiz_session_id", ASCENDING)]),
            IndexModel([("predicted_rank", ASCENDING)]),
            IndexModel([("predicted_percentile", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("target_exam", ASCENDING)]),
            IndexModel([("created_at", ASCENDING)]),
        ]


class PerformanceAnalytics(BaseDocument):
    """User performance analytics for better predictions."""
    
    user_id: str = Field(..., description="User ID")
    exam_category: str = Field(..., description="Exam category (e.g., CAT, JEE)")
    
    # Performance statistics
    total_mock_tests: int = Field(default=0, description="Total mock tests taken")
    average_percentile: float = Field(default=0.0, description="Average percentile across mocks")
    best_percentile: float = Field(default=0.0, description="Best percentile achieved")
    recent_percentile: float = Field(default=0.0, description="Most recent percentile")
    
    # Subject-wise analytics
    subject_strengths: List[str] = Field(default_factory=list, description="Strong subjects")
    subject_weaknesses: List[str] = Field(default_factory=list, description="Weak subjects")
    subject_trends: dict = Field(default_factory=dict, description="Subject-wise improvement trends")
    
    # Time management
    average_time_per_question: float = Field(default=0.0, description="Average time per question (seconds)")
    time_management_score: float = Field(default=0.0, description="Time management efficiency score")
    
    # Consistency metrics
    performance_consistency: float = Field(default=0.0, description="Consistency score (0-1)")
    improvement_rate: float = Field(default=0.0, description="Rate of improvement over time")
    
    # Last updated
    last_calculated: datetime = Field(default_factory=datetime.utcnow, description="Last calculation time")
    
    class Settings:
        name = "performance_analytics"
        indexes = [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("exam_category", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("exam_category", ASCENDING)], unique=True),
            IndexModel([("last_calculated", ASCENDING)]),
        ]


# Export all models
__all__ = [
    "Quiz",
    "Question", 
    "Answer",
    "QuizSession",
    "RealExamResult",
    "PredictionModel",
    "UserPrediction", 
    "PerformanceAnalytics",
    "DifficultyLevel",
    "QuestionType", 
    "SessionStatus",
    "QuizType"
]
