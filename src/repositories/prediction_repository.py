"""
Repository layer for prediction-related database operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId

from ..models.quiz import (
    UserPrediction, RealExamResult, PredictionModel, 
    PerformanceAnalytics, QuizSession, Quiz
)


class PredictionRepository:
    """Repository for prediction-related database operations."""
    
    async def save_user_prediction(self, prediction: UserPrediction) -> UserPrediction:
        """Save a user prediction to database."""
        return await prediction.insert()
    
    async def get_user_predictions(
        self, 
        user_id: str, 
        target_exam: str,
        limit: int = 10
    ) -> List[UserPrediction]:
        """Get user's prediction history."""
        return await UserPrediction.find(
            UserPrediction.user_id == user_id,
            UserPrediction.target_exam == target_exam
        ).sort(-UserPrediction.created_at).limit(limit).to_list()
    
    async def get_latest_prediction(
        self, 
        user_id: str, 
        target_exam: str
    ) -> Optional[UserPrediction]:
        """Get user's latest prediction for target exam."""
        return await UserPrediction.find_one(
            UserPrediction.user_id == user_id,
            UserPrediction.target_exam == target_exam
        ).sort(-UserPrediction.created_at)
    
    async def get_prediction_leaderboard(
        self, 
        target_exam: str, 
        limit: int = 50,
        min_confidence: float = 0.5
    ) -> List[UserPrediction]:
        """Get prediction leaderboard for target exam."""
        return await UserPrediction.find(
            UserPrediction.target_exam == target_exam,
            UserPrediction.percentile_confidence >= min_confidence
        ).sort(UserPrediction.predicted_rank).limit(limit).to_list()


class RealExamResultRepository:
    """Repository for real exam results."""
    
    async def save_exam_result(self, result: RealExamResult) -> RealExamResult:
        """Save real exam result."""
        return await result.insert()
    
    async def get_exam_results(
        self, 
        exam_name: str, 
        exam_year: int
    ) -> List[RealExamResult]:
        """Get all results for a specific exam."""
        return await RealExamResult.find(
            RealExamResult.exam_name == exam_name,
            RealExamResult.exam_year == exam_year
        ).to_list()
    
    async def get_user_exam_result(
        self, 
        user_id: str, 
        exam_name: str, 
        exam_year: int
    ) -> Optional[RealExamResult]:
        """Get user's result for specific exam."""
        return await RealExamResult.find_one(
            RealExamResult.user_id == user_id,
            RealExamResult.exam_name == exam_name,
            RealExamResult.exam_year == exam_year
        )
    
    async def get_percentile_distribution(
        self, 
        exam_name: str, 
        exam_year: int
    ) -> Dict[str, Any]:
        """Get percentile distribution for an exam."""
        pipeline = [
            {
                "$match": {
                    "exam_name": exam_name,
                    "exam_year": exam_year
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_percentile": {"$avg": "$overall_percentile"},
                    "min_percentile": {"$min": "$overall_percentile"},
                    "max_percentile": {"$max": "$overall_percentile"},
                    "total_candidates": {"$sum": 1},
                    "percentile_90": {"$percentile": {"input": "$overall_percentile", "p": [0.9]}},
                    "percentile_95": {"$percentile": {"input": "$overall_percentile", "p": [0.95]}},
                    "percentile_99": {"$percentile": {"input": "$overall_percentile", "p": [0.99]}}
                }
            }
        ]
        
        result = await RealExamResult.aggregate(pipeline).to_list()
        return result[0] if result else {}


class PerformanceAnalyticsRepository:
    """Repository for performance analytics."""
    
    async def save_analytics(self, analytics: PerformanceAnalytics) -> PerformanceAnalytics:
        """Save performance analytics."""
        return await analytics.insert()
    
    async def get_user_analytics(
        self, 
        user_id: str, 
        exam_category: str
    ) -> Optional[PerformanceAnalytics]:
        """Get user's performance analytics."""
        return await PerformanceAnalytics.find_one(
            PerformanceAnalytics.user_id == user_id,
            PerformanceAnalytics.exam_category == exam_category
        )
    
    async def update_user_analytics(
        self, 
        user_id: str, 
        exam_category: str, 
        updates: Dict[str, Any]
    ) -> Optional[PerformanceAnalytics]:
        """Update user's performance analytics."""
        analytics = await self.get_user_analytics(user_id, exam_category)
        
        if not analytics:
            # Create new analytics record
            analytics = PerformanceAnalytics(
                user_id=user_id,
                exam_category=exam_category,
                **updates
            )
            return await analytics.insert()
        
        # Update existing record
        for key, value in updates.items():
            setattr(analytics, key, value)
        
        analytics.last_calculated = datetime.utcnow()
        await analytics.save()
        return analytics
    
    async def calculate_user_analytics(
        self, 
        user_id: str, 
        exam_category: str
    ) -> PerformanceAnalytics:
        """Calculate and save comprehensive user analytics."""
        
        # Get user's quiz sessions for the exam category
        sessions = await QuizSession.find(
            QuizSession.user_id == user_id,
            QuizSession.status == "completed"
        ).to_list()
        
        # Filter sessions for relevant quizzes
        relevant_sessions = []
        for session in sessions:
            quiz = await Quiz.get(session.quiz_id)
            if quiz and exam_category.lower() in (quiz.category or "").lower():
                relevant_sessions.append(session)
        
        if not relevant_sessions:
            # Return default analytics
            return PerformanceAnalytics(
                user_id=user_id,
                exam_category=exam_category
            )
        
        # Calculate statistics
        percentiles = [s.percentage_score for s in relevant_sessions if s.percentage_score]
        
        total_mock_tests = len(relevant_sessions)
        average_percentile = sum(percentiles) / len(percentiles) if percentiles else 0
        best_percentile = max(percentiles) if percentiles else 0
        recent_percentile = percentiles[-1] if percentiles else 0
        
        # Calculate subject analytics
        subject_data = {}
        for session in relevant_sessions:
            if session.subject_scores:
                for subject, score_data in session.subject_scores.items():
                    if subject not in subject_data:
                        subject_data[subject] = []
                    
                    if isinstance(score_data, dict) and 'percentage' in score_data:
                        subject_data[subject].append(score_data['percentage'])
        
        # Determine strengths and weaknesses
        subject_strengths = []
        subject_weaknesses = []
        subject_trends = {}
        
        for subject, scores in subject_data.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                if avg_score >= 75:
                    subject_strengths.append(subject)
                elif avg_score < 50:
                    subject_weaknesses.append(subject)
                
                # Calculate trend
                if len(scores) >= 3:
                    recent_avg = sum(scores[-3:]) / 3
                    earlier_avg = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else avg_score
                    trend = "improving" if recent_avg > earlier_avg + 5 else "declining" if recent_avg < earlier_avg - 5 else "stable"
                    subject_trends[subject] = trend
        
        # Calculate time management
        time_scores = []
        for session in relevant_sessions:
            if session.time_taken_minutes and session.time_limit_minutes:
                efficiency = session.time_taken_minutes / session.time_limit_minutes
                time_scores.append(efficiency)
        
        average_time_per_question = 0  # Would need more detailed timing data
        time_management_score = 1 - abs(sum(time_scores) / len(time_scores) - 0.9) if time_scores else 0.8
        
        # Calculate consistency
        if len(percentiles) > 1:
            variance = sum((x - average_percentile) ** 2 for x in percentiles) / len(percentiles)
            performance_consistency = max(0, 1 - (variance / 1000))
        else:
            performance_consistency = 0.5
        
        # Calculate improvement rate
        if len(percentiles) >= 3:
            early_avg = sum(percentiles[:len(percentiles)//2]) / (len(percentiles)//2)
            late_avg = sum(percentiles[len(percentiles)//2:]) / (len(percentiles) - len(percentiles)//2)
            improvement_rate = (late_avg - early_avg) / 100  # Normalized improvement
        else:
            improvement_rate = 0
        
        # Create or update analytics
        analytics = PerformanceAnalytics(
            user_id=user_id,
            exam_category=exam_category,
            total_mock_tests=total_mock_tests,
            average_percentile=average_percentile,
            best_percentile=best_percentile,
            recent_percentile=recent_percentile,
            subject_strengths=subject_strengths,
            subject_weaknesses=subject_weaknesses,
            subject_trends=subject_trends,
            average_time_per_question=average_time_per_question,
            time_management_score=time_management_score,
            performance_consistency=performance_consistency,
            improvement_rate=improvement_rate,
            last_calculated=datetime.utcnow()
        )
        
        return await analytics.insert()


class PredictionModelRepository:
    """Repository for prediction models."""
    
    async def save_model(self, model: PredictionModel) -> PredictionModel:
        """Save prediction model."""
        return await model.insert()
    
    async def get_active_model(self, exam_name: str) -> Optional[PredictionModel]:
        """Get active prediction model for exam."""
        return await PredictionModel.find_one(
            PredictionModel.exam_name == exam_name,
            PredictionModel.is_active == True
        ).sort(-PredictionModel.created_at)
    
    async def get_all_models(self, exam_name: str) -> List[PredictionModel]:
        """Get all models for exam."""
        return await PredictionModel.find(
            PredictionModel.exam_name == exam_name
        ).sort(-PredictionModel.created_at).to_list()
    
    async def update_model_status(
        self, 
        model_id: str, 
        is_active: bool
    ) -> Optional[PredictionModel]:
        """Update model active status."""
        model = await PredictionModel.get(model_id)
        if model:
            model.is_active = is_active
            await model.save()
        return model
