"""
Quiz repository for MongoDB data access operations.
"""

from typing import List, Optional, Dict, Any
from pymongo import ASCENDING, DESCENDING

from ..models.quiz import Quiz, Question, Answer, QuizSession
from . import BaseRepository


class QuizRepository(BaseRepository[Quiz]):
    """Repository for Quiz operations."""
    
    def __init__(self):
        super().__init__(Quiz)
    
    async def get_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[Quiz]:
        """Get quizzes by category."""
        return await self.find_many(
            filters={"category": category, "is_active": True},
            skip=skip,
            limit=limit,
            sort={"created_at": DESCENDING}
        )
    
    async def get_by_difficulty(self, difficulty: str, skip: int = 0, limit: int = 100) -> List[Quiz]:
        """Get quizzes by difficulty level."""
        return await self.find_many(
            filters={"difficulty_level": difficulty, "is_active": True},
            skip=skip,
            limit=limit,
            sort={"created_at": DESCENDING}
        )
    
    async def search_quizzes(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Quiz]:
        """Search quizzes by title or description."""
        # Using MongoDB text search (requires text index)
        return await Quiz.find(
            {
                "$or": [
                    {"title": {"$regex": search_term, "$options": "i"}},
                    {"description": {"$regex": search_term, "$options": "i"}}
                ],
                "is_active": True
            }
        ).skip(skip).limit(limit).sort([("created_at", DESCENDING)]).to_list()


class QuestionRepository(BaseRepository[Question]):
    """Repository for Question operations."""
    
    def __init__(self):
        super().__init__(Question)
    
    async def get_by_quiz_id(self, quiz_id: str, only_active: bool = True) -> List[Question]:
        """Get all questions for a quiz."""
        filters = {"quiz_id": quiz_id}
        if only_active:
            filters["is_active"] = True
        
        return await self.find_many(
            filters=filters,
            sort={"order_index": ASCENDING}
        )
    
    async def get_question_by_order(self, quiz_id: str, order_index: int) -> Optional[Question]:
        """Get question by its order in the quiz."""
        return await self.find_one({
            "quiz_id": quiz_id,
            "order_index": order_index,
            "is_active": True
        })
    
    async def get_random_questions(self, quiz_id: str, count: int) -> List[Question]:
        """Get random questions from a quiz."""
        # MongoDB aggregation for random sampling
        pipeline = [
            {"$match": {"quiz_id": quiz_id, "is_active": True}},
            {"$sample": {"size": count}}
        ]
        
        result = await Question.aggregate(pipeline).to_list()
        return [Question(**doc) for doc in result]
    
    async def count_by_quiz(self, quiz_id: str) -> int:
        """Count questions in a quiz."""
        return await self.count({"quiz_id": quiz_id, "is_active": True})


class AnswerRepository(BaseRepository[Answer]):
    """Repository for Answer operations."""
    
    def __init__(self):
        super().__init__(Answer)
    
    async def get_user_answers(self, user_id: str, quiz_id: str) -> List[Answer]:
        """Get all answers for a user in a quiz."""
        return await self.find_many(
            filters={"user_id": user_id, "quiz_id": quiz_id},
            sort={"created_at": ASCENDING}
        )
    
    async def get_session_answers(self, session_id: str) -> List[Answer]:
        """Get all answers for a session."""
        return await self.find_many(
            filters={"session_id": session_id},
            sort={"created_at": ASCENDING}
        )
    
    async def get_answer_by_question(self, user_id: str, question_id: str) -> Optional[Answer]:
        """Get user's answer to a specific question."""
        return await self.find_one({
            "user_id": user_id,
            "question_id": question_id
        })
    
    async def get_quiz_statistics(self, quiz_id: str) -> Dict[str, Any]:
        """Get statistical data for a quiz."""
        # MongoDB aggregation for statistics
        pipeline = [
            {"$match": {"quiz_id": quiz_id}},
            {
                "$group": {
                    "_id": None,
                    "total_answers": {"$sum": 1},
                    "correct_answers": {
                        "$sum": {"$cond": [{"$eq": ["$is_correct", True]}, 1, 0]}
                    },
                    "total_points": {"$sum": "$points_earned"},
                    "unique_users": {"$addToSet": "$user_id"}
                }
            },
            {
                "$project": {
                    "total_answers": 1,
                    "correct_answers": 1,
                    "total_points": 1,
                    "unique_users_count": {"$size": "$unique_users"},
                    "accuracy_percentage": {
                        "$multiply": [
                            {"$divide": ["$correct_answers", "$total_answers"]},
                            100
                        ]
                    }
                }
            }
        ]
        
        result = await Answer.aggregate(pipeline).to_list()
        return result[0] if result else {
            "total_answers": 0,
            "correct_answers": 0,
            "total_points": 0,
            "unique_users_count": 0,
            "accuracy_percentage": 0
        }


class QuizSessionRepository(BaseRepository[QuizSession]):
    """Repository for QuizSession operations."""
    
    def __init__(self):
        super().__init__(QuizSession)
    
    async def get_user_sessions(self, user_id: str, quiz_id: Optional[str] = None) -> List[QuizSession]:
        """Get all sessions for a user, optionally filtered by quiz."""
        filters = {"user_id": user_id}
        if quiz_id:
            filters["quiz_id"] = quiz_id
        
        return await self.find_many(
            filters=filters,
            sort={"started_at": DESCENDING}
        )
    
    async def get_active_session(self, user_id: str, quiz_id: str) -> Optional[QuizSession]:
        """Get active session for a user and quiz."""
        return await self.find_one({
            "user_id": user_id,
            "quiz_id": quiz_id,
            "status": "in_progress"
        })
    
    async def get_leaderboard(self, quiz_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard for a quiz."""
        # MongoDB aggregation for leaderboard
        pipeline = [
            {
                "$match": {
                    "quiz_id": quiz_id,
                    "status": "completed"
                }
            },
            {
                "$group": {
                    "_id": "$user_id",
                    "best_score": {"$max": "$total_score"},
                    "best_percentage": {"$max": "$percentage_score"},
                    "fastest_time": {"$min": "$time_taken_minutes"},
                    "attempts": {"$sum": 1},
                    "last_attempt": {"$max": "$completed_at"}
                }
            },
            {
                "$project": {
                    "user_id": "$_id",
                    "total_score": "$best_score",
                    "percentage_score": "$best_percentage",
                    "time_taken_minutes": "$fastest_time",
                    "attempts": 1,
                    "completed_at": "$last_attempt"
                }
            },
            {"$sort": {"total_score": -1, "time_taken_minutes": 1}},
            {"$limit": limit}
        ]
        
        return await QuizSession.aggregate(pipeline).to_list()
    
    async def count_completed_sessions(self, quiz_id: str) -> int:
        """Count completed sessions for a quiz."""
        return await self.count({"quiz_id": quiz_id, "status": "completed"})
