"""
Quiz API endpoints for the MCQ Quiz Platform using MongoDB.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query

from ...services.quiz_service import QuizService, QuestionService, AnswerService, QuizSessionService
from ..schemas import (
    QuizCreate, QuizUpdate, QuizResponse, QuizListResponse,
    QuestionCreate, QuestionUpdate, QuestionResponse, QuestionResponsePublic,
    AnswerSubmit, AnswerResponse,
    QuizSessionStart, QuizSessionResponse, LeaderboardEntry,
    QuizStatistics, MessageResponse, BulkQuestionCreate, BulkOperationResponse
)

router = APIRouter(prefix="/api/v1/quiz", tags=["Quiz Management"])


# Quiz Endpoints
@router.post("/quizzes", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(quiz_data: QuizCreate):
    """Create a new quiz."""
    try:
        quiz_service = QuizService()
        quiz = await quiz_service.create_quiz(quiz_data.model_dump())
        return quiz
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create quiz: {str(e)}"
        )


@router.get("/quizzes", response_model=QuizListResponse)
async def get_quizzes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Get all quizzes with optional filtering."""
    try:
        quiz_service = QuizService()
        quizzes = await quiz_service.get_quizzes(
            skip=skip,
            limit=limit,
            category=category,
            difficulty=difficulty,
            search=search
        )
        
        return QuizListResponse(
            quizzes=quizzes,
            total=len(quizzes),
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quizzes: {str(e)}"
        )


@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: str):
    """Get a specific quiz by ID."""
    try:
        quiz_service = QuizService()
        quiz = await quiz_service.get_quiz(quiz_id)
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        return quiz
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quiz: {str(e)}"
        )


@router.put("/quizzes/{quiz_id}", response_model=QuizResponse)
async def update_quiz(quiz_id: str, quiz_data: QuizUpdate):
    """Update a quiz."""
    try:
        quiz_service = QuizService()
        quiz = await quiz_service.update_quiz(quiz_id, quiz_data.model_dump(exclude_unset=True))
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        return quiz
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update quiz: {str(e)}"
        )


@router.delete("/quizzes/{quiz_id}", response_model=MessageResponse)
async def delete_quiz(quiz_id: str):
    """Delete a quiz."""
    try:
        quiz_service = QuizService()
        deleted = await quiz_service.delete_quiz(quiz_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        return MessageResponse(message="Quiz deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete quiz: {str(e)}"
        )


@router.get("/quizzes/{quiz_id}/questions", response_model=List[QuestionResponsePublic])
async def get_quiz_questions(quiz_id: str):
    """Get all questions for a quiz."""
    try:
        question_service = QuestionService()
        questions = await question_service.get_quiz_questions(quiz_id)
        return questions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quiz questions: {str(e)}"
        )


# Question Endpoints
@router.post("/questions", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(question_data: QuestionCreate):
    """Create a new question."""
    try:
        question_service = QuestionService()
        question = await question_service.create_question(question_data.model_dump())
        return question
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create question: {str(e)}"
        )


@router.post("/questions/bulk", response_model=BulkOperationResponse, status_code=status.HTTP_201_CREATED)
async def create_questions_bulk(question_data: BulkQuestionCreate):
    """Create multiple questions in bulk."""
    try:
        question_service = QuestionService()
        created_questions = []
        errors = []
        
        for idx, q_data in enumerate(question_data.questions):
            try:
                question = await question_service.create_question(q_data.model_dump())
                created_questions.append(question)
            except Exception as e:
                errors.append(f"Question {idx + 1}: {str(e)}")
        
        return BulkOperationResponse(
            created=len(created_questions),
            errors=errors,
            total=len(question_data.questions)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create questions: {str(e)}"
        )


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: str):
    """Get a specific question by ID."""
    try:
        question_service = QuestionService()
        question = await question_service.get_question(question_id)
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        return question
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get question: {str(e)}"
        )


@router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: str, question_data: QuestionUpdate):
    """Update a question."""
    try:
        question_service = QuestionService()
        question = await question_service.update_question(question_id, question_data.model_dump(exclude_unset=True))
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        return question
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update question: {str(e)}"
        )


@router.delete("/questions/{question_id}", response_model=MessageResponse)
async def delete_question(question_id: str):
    """Delete a question."""
    try:
        question_service = QuestionService()
        deleted = await question_service.delete_question(question_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        return MessageResponse(message="Question deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete question: {str(e)}"
        )


# Answer Endpoints
@router.post("/answers", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def submit_answer(answer_data: AnswerSubmit):
    """Submit an answer to a question."""
    try:
        answer_service = AnswerService()
        answer = await answer_service.submit_answer(
            user_id=answer_data.user_id,
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
async def get_user_sessions(user_id: str, quiz_id: Optional[str] = Query(None)):
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
async def get_quiz_leaderboard(quiz_id: str, limit: int = Query(10, ge=1, le=100)):
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
