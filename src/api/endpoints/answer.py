"""
Answer and Session API endpoints for the MCQ Quiz Platform using MongoDB.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Query, Header

from ...services.quiz_service import AnswerService, QuizSessionService
from ..schemas import (
    AnswerSubmit, AnswerResponse,
    QuizSessionStart, QuizSessionResponse, LeaderboardEntry,
    QuizStatistics, MessageResponse
)

router = APIRouter(prefix="/api/v1", tags=["Quiz Interaction"])


# Answer Endpoints
@router.post("/submit-answer", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def submit_answer(
    answer_data: AnswerSubmit,
    user_id: str = Header(..., description="User ID from authentication")
):
    """Submit an answer to a question."""
    try:
        answer_service = AnswerService()
        answer = await answer_service.submit_answer(
            user_id=user_id,
            question_id=answer_data.question_id,
            selected_answers=answer_data.selected_answers,
            session_id=answer_data.session_id,
            time_taken_seconds=answer_data.time_taken_seconds
        )
        return answer
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit answer: {str(e)}"
        )


@router.get("/users/{user_id}/quizzes/{quiz_id}/answers", response_model=List[AnswerResponse])
async def get_user_answers(user_id: str, quiz_id: str):
    """Get all answers for a user in a quiz."""
    try:
        answer_service = AnswerService()
        answers = await answer_service.get_user_answers(user_id, quiz_id)
        return answers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user answers: {str(e)}"
        )


@router.get("/sessions/{session_id}/answers", response_model=List[AnswerResponse])
async def get_session_answers(session_id: str):
    """Get all answers for a quiz session."""
    try:
        answer_service = AnswerService()
        answers = await answer_service.get_session_answers(session_id)
        return answers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session answers: {str(e)}"
        )


@router.get("/quizzes/{quiz_id}/statistics", response_model=QuizStatistics)
async def get_quiz_statistics(quiz_id: str):
    """Get statistical data for a quiz."""
    try:
        answer_service = AnswerService()
        stats = await answer_service.get_quiz_statistics(quiz_id)
        return QuizStatistics(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quiz statistics: {str(e)}"
        )


# Quiz Session Endpoints
@router.post("/sessions", response_model=QuizSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_quiz_session(session_data: QuizSessionStart):
    """Start a new quiz session."""
    try:
        session_service = QuizSessionService()
        session = await session_service.start_quiz_session(
            user_id=session_data.user_id,
            quiz_id=session_data.quiz_id
        )
        return session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start quiz session: {str(e)}"
        )


@router.put("/sessions/{session_id}/complete", response_model=QuizSessionResponse)
async def complete_quiz_session(session_id: str):
    """Complete a quiz session."""
    try:
        session_service = QuizSessionService()
        session = await session_service.complete_quiz_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz session not found"
            )
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete quiz session: {str(e)}"
        )


@router.put("/sessions/{session_id}/abandon", response_model=QuizSessionResponse)
async def abandon_quiz_session(session_id: str):
    """Abandon a quiz session."""
    try:
        session_service = QuizSessionService()
        session = await session_service.abandon_quiz_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz session not found"
            )
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to abandon quiz session: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=QuizSessionResponse)
async def get_quiz_session(session_id: str):
    """Get a quiz session by ID."""
    try:
        session_service = QuizSessionService()
        session = await session_service.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz session not found"
            )
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quiz session: {str(e)}"
        )


@router.get("/users/{user_id}/sessions", response_model=List[QuizSessionResponse])
async def get_user_sessions(
    user_id: str,
    quiz_id: str = Query(None, description="Filter by quiz ID")
):
    """Get all sessions for a user."""
    try:
        session_service = QuizSessionService()
        sessions = await session_service.get_user_sessions(user_id, quiz_id)
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user sessions: {str(e)}"
        )


@router.get("/quizzes/{quiz_id}/leaderboard", response_model=List[LeaderboardEntry])
async def get_quiz_leaderboard(
    quiz_id: str,
    limit: int = Query(10, ge=1, le=100, description="Maximum number of entries")
):
    """Get leaderboard for a quiz."""
    try:
        session_service = QuizSessionService()
        leaderboard = await session_service.get_leaderboard(quiz_id, limit)
        return [LeaderboardEntry(**entry) for entry in leaderboard]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quiz leaderboard: {str(e)}"
        )


# Session Management Endpoints
@router.get("/sessions", response_model=List[QuizSessionResponse])
async def get_all_sessions(
    skip: int = Query(0, ge=0, description="Number of sessions to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of sessions to return"),
    status_filter: str = Query(None, description="Filter by session status")
):
    """Get all quiz sessions with optional filtering."""
    try:
        session_service = QuizSessionService()
        # This would need to be implemented in the service layer
        # For now, return empty list or implement basic functionality
        return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sessions: {str(e)}"
        )


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def delete_quiz_session(session_id: str):
    """Delete a quiz session (admin only)."""
    try:
        session_service = QuizSessionService()
        # This would need to be implemented in the service layer
        # For now, return a message indicating it's not implemented
        return MessageResponse(message="Session deletion not implemented yet")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


# Bulk operations
@router.post("/submit-answers/bulk", response_model=List[AnswerResponse])
async def submit_answers_bulk(
    answers_data: List[AnswerSubmit],
    user_id: str = Header(..., description="User ID from authentication")
):
    """Submit multiple answers at once."""
    try:
        answer_service = AnswerService()
        results = []
        errors = []
        
        for idx, answer_data in enumerate(answers_data):
            try:
                answer = await answer_service.submit_answer(
                    user_id=user_id,
                    question_id=answer_data.question_id,
                    selected_answers=answer_data.selected_answers,
                    session_id=answer_data.session_id,
                    time_taken_seconds=answer_data.time_taken_seconds
                )
                results.append(answer)
            except Exception as e:
                errors.append(f"Answer {idx + 1}: {str(e)}")
        
        if errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Some answers failed to submit: {'; '.join(errors)}"
            )
        
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit bulk answers: {str(e)}"
        )
