"""
Service layer for quiz-related business logic using MongoDB.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.quiz import Quiz, Question, Answer, QuizSession
from ..repositories.quiz_repository import (
    QuizRepository, QuestionRepository, AnswerRepository, QuizSessionRepository
)


class QuizService:
    """Service for quiz-related business logic."""
    
    def __init__(self):
        self.quiz_repository = QuizRepository()
        self.question_repository = QuestionRepository()
        self.answer_repository = AnswerRepository()
        self.session_repository = QuizSessionRepository()
    
    async def create_quiz(self, quiz_data: Dict[str, Any]) -> Quiz:
        """Create a new quiz."""
        quiz = await self.quiz_repository.create(quiz_data)
        return quiz
    
    async def get_quiz(self, quiz_id: str) -> Optional[Quiz]:
        """Get a quiz by ID."""
        return await self.quiz_repository.get_by_id(quiz_id)
    
    async def get_quiz_with_questions(self, quiz_id: str) -> Optional[Quiz]:
        """Get a quiz with all its questions."""
        quiz = await self.quiz_repository.get_by_id(quiz_id)
        if quiz:
            quiz.questions = await self.question_repository.get_by_quiz_id(quiz_id)
        return quiz
    
    async def get_quizzes(
        self, 
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Quiz]:
        """Get quizzes with optional filtering."""
        if category:
            return await self.quiz_repository.get_by_category(category, skip, limit)
        elif difficulty:
            return await self.quiz_repository.get_by_difficulty(difficulty, skip, limit)
        elif search:
            return await self.quiz_repository.search_quizzes(search, skip, limit)
        else:
            return await self.quiz_repository.get_all(skip, limit, filters={"is_active": True})
    
    async def update_quiz(self, quiz_id: str, quiz_data: Dict[str, Any]) -> Optional[Quiz]:
        """Update a quiz."""
        return await self.quiz_repository.update(quiz_id, quiz_data)
    
    async def delete_quiz(self, quiz_id: str) -> bool:
        """Delete a quiz."""
        return await self.quiz_repository.delete(quiz_id)


class QuestionService:
    """Service for question-related business logic."""
    
    def __init__(self):
        self.question_repository = QuestionRepository()
        self.quiz_repository = QuizRepository()
    
    async def create_question(self, question_data: Dict[str, Any]) -> Question:
        """Create a new question and update quiz question count."""
        question = await self.question_repository.create(question_data)
        
        # Update quiz total_questions count
        quiz_id = question_data["quiz_id"]
        count = await self.question_repository.count_by_quiz(quiz_id)
        await self.quiz_repository.update(quiz_id, {"total_questions": count})
        
        return question
    
    async def get_question(self, question_id: str) -> Optional[Question]:
        """Get a question by ID."""
        return await self.question_repository.get_by_id(question_id)
    
    async def get_quiz_questions(self, quiz_id: str, only_active: bool = True) -> List[Question]:
        """Get all questions for a quiz."""
        return await self.question_repository.get_by_quiz_id(quiz_id, only_active)
    
    async def get_question_by_order(self, quiz_id: str, order_index: int) -> Optional[Question]:
        """Get question by its order in the quiz."""
        return await self.question_repository.get_question_by_order(quiz_id, order_index)
    
    async def get_random_questions(self, quiz_id: str, count: int) -> List[Question]:
        """Get random questions from a quiz."""
        return await self.question_repository.get_random_questions(quiz_id, count)
    
    async def update_question(self, question_id: str, question_data: Dict[str, Any]) -> Optional[Question]:
        """Update a question."""
        return await self.question_repository.update(question_id, question_data)
    
    async def delete_question(self, question_id: str) -> bool:
        """Delete a question and update quiz question count."""
        question = await self.question_repository.get_by_id(question_id)
        if not question:
            return False
        
        quiz_id = question.quiz_id
        deleted = await self.question_repository.delete(question_id)
        
        if deleted:
            # Update quiz total_questions count
            count = await self.question_repository.count_by_quiz(quiz_id)
            await self.quiz_repository.update(quiz_id, {"total_questions": count})
        
        return deleted


class AnswerService:
    """Service for answer-related business logic."""
    
    def __init__(self):
        self.answer_repository = AnswerRepository()
        self.question_repository = QuestionRepository()
        self.session_repository = QuizSessionRepository()
    
    async def submit_answer(
        self, 
        user_id: str, 
        question_id: str, 
        selected_answers: List[str],
        session_id: Optional[str] = None,
        time_taken_seconds: Optional[int] = None
    ) -> Answer:
        """Submit an answer to a question."""
        # Get the question to validate answer
        question = await self.question_repository.get_by_id(question_id)
        if not question:
            raise ValueError("Question not found")
        
        # Check if answer is correct (compare lists)
        correct_answers_set = set(question.correct_answers)
        selected_answers_set = set(selected_answers)
        is_correct = correct_answers_set == selected_answers_set
        points_earned = question.points if is_correct else 0
        
        # Create answer record
        answer_data = {
            "user_id": user_id,
            "quiz_id": question.quiz_id,
            "question_id": question_id,
            "selected_answers": selected_answers,
            "is_correct": is_correct,
            "points_earned": points_earned,
            "time_taken_seconds": time_taken_seconds,
            "session_id": session_id
        }
        
        # Check if user already answered this question
        existing_answer = await self.answer_repository.get_answer_by_question(user_id, question_id)
        if existing_answer:
            # Update existing answer
            answer = await self.answer_repository.update(existing_answer.id, answer_data)
        else:
            # Create new answer
            answer = await self.answer_repository.create(answer_data)
        
        # Update session if provided
        if session_id:
            await self._update_session_progress(session_id)
        
        return answer
    
    async def get_user_answers(self, user_id: str, quiz_id: str) -> List[Answer]:
        """Get all answers for a user in a quiz."""
        return await self.answer_repository.get_user_answers(user_id, quiz_id)
    
    async def get_session_answers(self, session_id: str) -> List[Answer]:
        """Get all answers for a session."""
        return await self.answer_repository.get_session_answers(session_id)
    
    async def get_quiz_statistics(self, quiz_id: str) -> Dict[str, Any]:
        """Get statistical data for a quiz."""
        return await self.answer_repository.get_quiz_statistics(quiz_id)
    
    async def _update_session_progress(self, session_id: str):
        """Update quiz session progress based on answers."""
        session = await self.session_repository.get_by_id(session_id)
        if not session:
            return
        
        answers = await self.answer_repository.get_session_answers(session_id)
        
        # Calculate progress
        total_score = sum(answer.points_earned for answer in answers)
        correct_count = sum(1 for answer in answers if answer.is_correct)
        
        # Update session
        session_data = {
            "total_score": total_score,
            "questions_answered": len(answers),
            "correct_answers": correct_count,
            "updated_at": datetime.utcnow()
        }
        
        # Calculate percentage if max score is available
        if session.max_possible_score > 0:
            session_data["percentage_score"] = (total_score / session.max_possible_score) * 100
        
        await self.session_repository.update(session_id, session_data)


class QuizSessionService:
    """Service for quiz session management."""
    
    def __init__(self):
        self.session_repository = QuizSessionRepository()
        self.quiz_repository = QuizRepository()
        self.question_repository = QuestionRepository()
    
    async def start_quiz_session(self, user_id: str, quiz_id: str) -> QuizSession:
        """Start a new quiz session."""
        # Check if there's already an active session
        active_session = await self.session_repository.get_active_session(user_id, quiz_id)
        if active_session:
            return active_session
        
        # Get quiz to calculate max possible score
        quiz = await self.quiz_repository.get_by_id(quiz_id)
        if not quiz:
            raise ValueError("Quiz not found")
        
        questions = await self.question_repository.get_by_quiz_id(quiz_id)
        max_possible_score = sum(q.points for q in questions if q.is_active)
        
        # Create new session
        session_data = {
            "user_id": user_id,
            "quiz_id": quiz_id,
            "status": "in_progress",
            "started_at": datetime.utcnow(),
            "time_limit_minutes": quiz.time_limit_minutes,
            "max_possible_score": max_possible_score,
            "total_questions": len(questions)
        }
        
        return await self.session_repository.create(session_data)
    
    async def complete_quiz_session(self, session_id: str) -> Optional[QuizSession]:
        """Complete a quiz session and calculate final score."""
        session = await self.session_repository.get_by_id(session_id)
        if not session:
            return None
        
        # Calculate final metrics
        completion_time = datetime.utcnow()
        time_taken_minutes = int((completion_time - session.started_at).total_seconds() / 60) if session.started_at else 0
        
        percentage_score = (
            (session.total_score / session.max_possible_score * 100) 
            if session.max_possible_score > 0 else 0
        )
        
        # Get quiz passing score to determine if passed
        quiz = await self.quiz_repository.get_by_id(session.quiz_id)
        is_passed = (
            percentage_score >= quiz.passing_score 
            if quiz and quiz.passing_score is not None 
            else None
        )
        
        # Update session
        session_data = {
            "status": "completed",
            "completed_at": completion_time,
            "time_taken_minutes": time_taken_minutes,
            "percentage_score": percentage_score,
            "is_passed": is_passed,
            "updated_at": datetime.utcnow()
        }
        
        return await self.session_repository.update(session_id, session_data)
    
    async def abandon_quiz_session(self, session_id: str) -> Optional[QuizSession]:
        """Mark a quiz session as abandoned."""
        session_data = {
            "status": "abandoned",
            "completed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        return await self.session_repository.update(session_id, session_data)
    
    async def get_user_sessions(self, user_id: str, quiz_id: Optional[str] = None) -> List[QuizSession]:
        """Get all sessions for a user."""
        return await self.session_repository.get_user_sessions(user_id, quiz_id)
    
    async def get_quiz_sessions(self, quiz_id: str, skip: int = 0, limit: int = 100) -> List[QuizSession]:
        """Get all sessions for a quiz."""
        return await self.session_repository.get_quiz_sessions(quiz_id, skip, limit)
    
    async def get_leaderboard(self, quiz_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard for a quiz."""
        return await self.session_repository.get_leaderboard(quiz_id, limit)
    
    async def get_session(self, session_id: str) -> Optional[QuizSession]:
        """Get a session by ID."""
        return await self.session_repository.get_by_id(session_id)
