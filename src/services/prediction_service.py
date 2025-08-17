"""
Prediction Service for Mock Test Analytics and Future Performance Prediction.

This service provides predictive analytics for mock test takers, including:
- Predicted rank based on historical data
- Predicted percentile 
- Subject-wise performance predictions
- Improvement suggestions
"""

import statistics
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..models.quiz import (
    Quiz, QuizSession, Question, Answer, 
    RealExamResult, UserPrediction, PerformanceAnalytics,
    QuizType
)
from ..repositories.quiz_repository import (
    QuizRepository, QuizSessionRepository, AnswerRepository
)
from ..repositories.prediction_repository import (
    PredictionRepository, RealExamResultRepository, 
    PerformanceAnalyticsRepository, PredictionModelRepository
)


@dataclass
class PredictionResult:
    """Structured prediction result."""
    predicted_rank: int
    predicted_percentile: float
    subject_percentiles: Dict[str, float]
    confidence_score: float
    improvement_suggestions: List[str]
    performance_trend: str
    expected_score_range: Dict[str, float]


@dataclass
class SubjectAnalysis:
    """Subject-wise performance analysis."""
    subject: str
    current_percentile: float
    predicted_percentile: float
    accuracy_trend: str  # "improving", "declining", "stable"
    strength_level: str  # "strong", "moderate", "weak"
    recommendations: List[str]


class PredictionService:
    """Service for generating predictive analytics for mock test takers."""
    
    def __init__(self):
        self.quiz_repository = QuizRepository()
        self.session_repository = QuizSessionRepository()
        self.answer_repository = AnswerRepository()
        self.prediction_repository = PredictionRepository()
        self.exam_result_repository = RealExamResultRepository()
        self.analytics_repository = PerformanceAnalyticsRepository()
        self.model_repository = PredictionModelRepository()
    
    async def generate_prediction(
        self, 
        user_id: str, 
        target_exam: str,
        quiz_session_id: Optional[str] = None
    ) -> PredictionResult:
        """
        Generate comprehensive prediction for a user's performance in target exam.
        
        Args:
            user_id: ID of the user
            target_exam: Target exam (e.g., "CAT 2025")
            quiz_session_id: Specific session to base prediction on (optional)
            
        Returns:
            PredictionResult with all predictions
        """
        # Get user's mock test history
        mock_sessions = await self._get_user_mock_sessions(user_id, target_exam)
        
        if len(mock_sessions) < 3:
            return await self._generate_preliminary_prediction(user_id, mock_sessions, target_exam)
        
        # Analyze performance trends
        performance_trend = await self._analyze_performance_trend(mock_sessions)
        
        # Calculate predicted rank and percentile
        predicted_rank, predicted_percentile = await self._calculate_rank_percentile_prediction(
            user_id, mock_sessions, target_exam
        )
        
        # Calculate subject-wise predictions
        subject_percentiles = await self._calculate_subject_predictions(
            user_id, mock_sessions, target_exam
        )
        
        # Generate improvement suggestions
        suggestions = await self._generate_improvement_suggestions(
            user_id, mock_sessions, subject_percentiles
        )
        
        # Calculate confidence score
        confidence = await self._calculate_prediction_confidence(mock_sessions)
        
        # Calculate expected score range
        score_range = await self._calculate_score_range(mock_sessions, confidence)
        
        return PredictionResult(
            predicted_rank=predicted_rank,
            predicted_percentile=predicted_percentile,
            subject_percentiles=subject_percentiles,
            confidence_score=confidence,
            improvement_suggestions=suggestions,
            performance_trend=performance_trend,
            expected_score_range=score_range
        )
    
    async def _get_user_mock_sessions(self, user_id: str, target_exam: str) -> List[QuizSession]:
        """Get all mock test sessions for a user relevant to target exam."""
        # Get recent mock sessions (last 6 months)
        cutoff_date = datetime.utcnow() - timedelta(days=180)
        
        sessions = await QuizSession.find(
            QuizSession.user_id == user_id,
            QuizSession.status == "completed",
            QuizSession.started_at >= cutoff_date
        ).to_list()
        
        # Filter for mock tests related to target exam
        relevant_sessions = []
        for session in sessions:
            quiz = await Quiz.get(session.quiz_id)
            if quiz and quiz.quiz_type == QuizType.MOCK_TEST:
                # Check if quiz is relevant to target exam (e.g., CAT mocks for CAT 2025)
                exam_type = target_exam.split()[0]  # Extract "CAT" from "CAT 2025"
                if exam_type.lower() in quiz.title.lower() or exam_type.lower() in quiz.category.lower():
                    relevant_sessions.append(session)
        
        return sorted(relevant_sessions, key=lambda x: x.started_at)
    
    async def _analyze_performance_trend(self, sessions: List[QuizSession]) -> str:
        """Analyze whether performance is improving, declining, or stable."""
        if len(sessions) < 3:
            return "insufficient_data"
        
        recent_scores = [s.percentage_score for s in sessions[-5:] if s.percentage_score]
        older_scores = [s.percentage_score for s in sessions[:-5] if s.percentage_score]
        
        if not recent_scores or not older_scores:
            return "insufficient_data"
        
        recent_avg = statistics.mean(recent_scores)
        older_avg = statistics.mean(older_scores)
        
        improvement = recent_avg - older_avg
        
        if improvement > 5:
            return "improving"
        elif improvement < -5:
            return "declining"
        else:
            return "stable"
    
    async def _calculate_rank_percentile_prediction(
        self, 
        user_id: str, 
        sessions: List[QuizSession], 
        target_exam: str
    ) -> Tuple[int, float]:
        """Calculate predicted rank and percentile based on mock performance."""
        
        # Get user's average performance metrics
        avg_percentile = statistics.mean([s.percentage_score for s in sessions if s.percentage_score])
        recent_percentiles = [s.percentage_score for s in sessions[-3:] if s.percentage_score]
        recent_avg = statistics.mean(recent_percentiles) if recent_percentiles else avg_percentile
        
        # Weight recent performance more heavily
        weighted_percentile = (recent_avg * 0.7) + (avg_percentile * 0.3)
        
        # Apply trend adjustment
        trend = await self._analyze_performance_trend(sessions)
        if trend == "improving":
            weighted_percentile += 3  # Optimistic adjustment
        elif trend == "declining":
            weighted_percentile -= 2  # Conservative adjustment
        
        # Ensure percentile is within bounds
        predicted_percentile = max(0, min(100, weighted_percentile))
        
        # Convert percentile to rank (assuming 100,000 candidates for CAT)
        total_candidates = await self._get_estimated_candidates(target_exam)
        predicted_rank = int(total_candidates * (100 - predicted_percentile) / 100)
        predicted_rank = max(1, predicted_rank)
        
        return predicted_rank, predicted_percentile
    
    async def _calculate_subject_predictions(
        self, 
        user_id: str, 
        sessions: List[QuizSession], 
        target_exam: str
    ) -> Dict[str, float]:
        """Calculate subject-wise percentile predictions."""
        subject_predictions = {}
        
        # Get all subjects from recent sessions
        all_subjects = set()
        for session in sessions:
            if session.subject_scores:
                all_subjects.update(session.subject_scores.keys())
        
        for subject in all_subjects:
            subject_scores = []
            for session in sessions:
                if session.subject_scores and subject in session.subject_scores:
                    score_data = session.subject_scores[subject]
                    if isinstance(score_data, dict) and 'percentage' in score_data:
                        subject_scores.append(score_data['percentage'])
            
            if subject_scores:
                # Calculate weighted average (recent performance weighted more)
                if len(subject_scores) >= 3:
                    recent_avg = statistics.mean(subject_scores[-3:])
                    overall_avg = statistics.mean(subject_scores)
                    predicted_percentile = (recent_avg * 0.7) + (overall_avg * 0.3)
                else:
                    predicted_percentile = statistics.mean(subject_scores)
                
                # Apply subject-specific adjustments based on difficulty patterns
                predicted_percentile = await self._apply_subject_adjustments(
                    subject, predicted_percentile, subject_scores
                )
                
                subject_predictions[subject] = max(0, min(100, predicted_percentile))
        
        return subject_predictions
    
    async def _apply_subject_adjustments(
        self, 
        subject: str, 
        base_percentile: float, 
        historical_scores: List[float]
    ) -> float:
        """Apply subject-specific adjustments based on historical patterns."""
        
        # Calculate consistency (lower variance = more predictable)
        if len(historical_scores) > 1:
            variance = statistics.variance(historical_scores)
            consistency_factor = max(0.9, 1 - (variance / 1000))  # Reduce prediction if inconsistent
        else:
            consistency_factor = 0.95
        
        # Subject difficulty adjustments (based on typical CAT patterns)
        difficulty_adjustments = {
            "quantitative_aptitude": 0,  # Baseline
            "verbal_ability": -1,  # Slightly more unpredictable
            "data_interpretation": 1,  # More consistent if practiced
            "logical_reasoning": -0.5,  # Moderate unpredictability
        }
        
        subject_key = subject.lower().replace(" ", "_")
        difficulty_adj = difficulty_adjustments.get(subject_key, 0)
        
        adjusted_percentile = base_percentile * consistency_factor + difficulty_adj
        return adjusted_percentile
    
    async def _generate_improvement_suggestions(
        self, 
        user_id: str, 
        sessions: List[QuizSession], 
        subject_predictions: Dict[str, float]
    ) -> List[str]:
        """Generate personalized improvement suggestions."""
        suggestions = []
        
        # Identify weak subjects
        weak_subjects = [
            subject for subject, percentile in subject_predictions.items() 
            if percentile < 70
        ]
        
        # Analyze time management
        avg_time_efficiency = await self._calculate_time_efficiency(sessions)
        if avg_time_efficiency < 0.8:
            suggestions.append(
                "Focus on time management - practice solving questions within time limits"
            )
        
        # Subject-specific suggestions
        for subject in weak_subjects:
            percentile = subject_predictions[subject]
            if percentile < 50:
                suggestions.append(
                    f"Priority: Strengthen {subject} fundamentals - aim for 60+ percentile"
                )
            elif percentile < 70:
                suggestions.append(
                    f"Focus on advanced {subject} topics to push above 70 percentile"
                )
        
        # Consistency suggestions
        consistency = await self._calculate_consistency_score(sessions)
        if consistency < 0.7:
            suggestions.append(
                "Work on consistency - maintain regular practice schedule"
            )
        
        # Recent performance suggestions
        trend = await self._analyze_performance_trend(sessions)
        if trend == "declining":
            suggestions.append(
                "Review recent weak areas and adjust study strategy"
            )
        elif trend == "stable" and subject_predictions:
            avg_pred = statistics.mean(subject_predictions.values())
            if avg_pred < 80:
                suggestions.append(
                    "Push for breakthrough - focus on accuracy improvement"
                )
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    async def _calculate_prediction_confidence(self, sessions: List[QuizSession]) -> float:
        """Calculate confidence score for predictions."""
        if len(sessions) < 3:
            return 0.3
        
        # Factor 1: Number of mock tests
        test_count_factor = min(1.0, len(sessions) / 10)
        
        # Factor 2: Consistency of performance
        consistency_factor = await self._calculate_consistency_score(sessions)
        
        # Factor 3: Recency of data
        latest_session = max(sessions, key=lambda x: x.started_at)
        days_since_last = (datetime.utcnow() - latest_session.started_at).days
        recency_factor = max(0.5, 1 - (days_since_last / 90))  # Decay over 90 days
        
        # Factor 4: Completeness of data
        complete_sessions = [s for s in sessions if s.percentage_score and s.subject_scores]
        completeness_factor = len(complete_sessions) / len(sessions)
        
        confidence = (
            test_count_factor * 0.3 + 
            consistency_factor * 0.3 + 
            recency_factor * 0.2 + 
            completeness_factor * 0.2
        )
        
        return min(0.95, max(0.1, confidence))
    
    async def _calculate_consistency_score(self, sessions: List[QuizSession]) -> float:
        """Calculate how consistent the user's performance is."""
        scores = [s.percentage_score for s in sessions if s.percentage_score]
        if len(scores) < 2:
            return 0.5
        
        mean_score = statistics.mean(scores)
        if mean_score == 0:
            return 0.1
        
        variance = statistics.variance(scores)
        coefficient_of_variation = (variance ** 0.5) / mean_score
        
        # Convert to consistency score (lower CV = higher consistency)
        consistency = max(0, 1 - (coefficient_of_variation / 0.5))
        return min(1.0, consistency)
    
    async def _calculate_time_efficiency(self, sessions: List[QuizSession]) -> float:
        """Calculate average time efficiency across sessions."""
        efficiencies = []
        
        for session in sessions:
            if session.time_taken_minutes and session.time_limit_minutes:
                if session.time_limit_minutes > 0:
                    efficiency = min(1.0, session.time_taken_minutes / session.time_limit_minutes)
                    # Good efficiency is using 80-95% of time
                    if 0.8 <= efficiency <= 0.95:
                        efficiencies.append(1.0)
                    elif efficiency < 0.8:
                        efficiencies.append(efficiency / 0.8)  # Penalize rushing
                    else:
                        efficiencies.append(0.95 / efficiency)  # Penalize overtime
        
        return statistics.mean(efficiencies) if efficiencies else 0.8
    
    async def _calculate_score_range(
        self, 
        sessions: List[QuizSession], 
        confidence: float
    ) -> Dict[str, float]:
        """Calculate expected score range based on historical performance."""
        scores = [s.percentage_score for s in sessions if s.percentage_score]
        if not scores:
            return {"min": 0.0, "max": 100.0}
        
        mean_score = statistics.mean(scores)
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 10
        
        # Confidence interval based on prediction confidence
        margin = std_dev * (2 - confidence)  # Higher confidence = smaller margin
        
        min_score = max(0, mean_score - margin)
        max_score = min(100, mean_score + margin)
        
        return {
            "min": round(min_score, 2),
            "max": round(max_score, 2),
            "expected": round(mean_score, 2)
        }
    
    async def _get_estimated_candidates(self, target_exam: str) -> int:
        """Get estimated number of candidates for target exam."""
        # Default estimates for major exams
        estimates = {
            "CAT": 200000,
            "JEE": 1000000,
            "NEET": 1500000,
            "GATE": 800000,
        }
        
        exam_type = target_exam.split()[0].upper()
        return estimates.get(exam_type, 100000)
    
    async def _generate_preliminary_prediction(
        self, 
        user_id: str, 
        sessions: List[QuizSession], 
        target_exam: str
    ) -> PredictionResult:
        """Generate preliminary prediction for users with limited data."""
        if not sessions:
            return PredictionResult(
                predicted_rank=50000,
                predicted_percentile=50.0,
                subject_percentiles={},
                confidence_score=0.1,
                improvement_suggestions=[
                    "Take more mock tests to get accurate predictions",
                    "Focus on building strong fundamentals in all subjects"
                ],
                performance_trend="insufficient_data",
                expected_score_range={"min": 0.0, "max": 100.0, "expected": 50.0}
            )
        
        # Use available data but with low confidence
        latest_session = sessions[-1]
        base_percentile = latest_session.percentage_score or 50.0
        
        total_candidates = await self._get_estimated_candidates(target_exam)
        predicted_rank = int(total_candidates * (100 - base_percentile) / 100)
        
        return PredictionResult(
            predicted_rank=predicted_rank,
            predicted_percentile=base_percentile,
            subject_percentiles=latest_session.subject_scores or {},
            confidence_score=0.3,
            improvement_suggestions=[
                "Take at least 3 more mock tests for better predictions",
                "Focus on identifying strengths and weaknesses"
            ],
            performance_trend="preliminary",
            expected_score_range={
                "min": max(0, base_percentile - 20),
                "max": min(100, base_percentile + 20),
                "expected": base_percentile
            }
        )

    async def save_prediction(
        self, 
        user_id: str, 
        quiz_session_id: str, 
        prediction: PredictionResult,
        target_exam: str
    ) -> UserPrediction:
        """Save prediction result to database."""
        user_prediction = UserPrediction(
            user_id=user_id,
            quiz_session_id=quiz_session_id,
            target_exam=target_exam,
            prediction_model_id="mock_test_predictor_v1",
            predicted_rank=prediction.predicted_rank,
            predicted_percentile=prediction.predicted_percentile,
            rank_confidence=prediction.confidence_score,
            percentile_confidence=prediction.confidence_score,
            subject_percentiles=prediction.subject_percentiles,
            subject_confidence={
                subject: prediction.confidence_score 
                for subject in prediction.subject_percentiles
            },
            based_on_mock_tests=[quiz_session_id],
            improvement_suggestions=prediction.improvement_suggestions,
            performance_trend=prediction.performance_trend,
            expected_score_range=prediction.expected_score_range
        )
        
        return await self.prediction_repository.save_user_prediction(user_prediction)

    async def get_user_prediction_history(
        self, 
        user_id: str, 
        target_exam: str
    ) -> List[UserPrediction]:
        """Get prediction history for a user."""
        return await self.prediction_repository.get_user_predictions(
            user_id=user_id,
            target_exam=target_exam
        )
