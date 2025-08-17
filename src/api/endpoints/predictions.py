"""
Prediction API endpoints for mock test analytics and future performance prediction.
"""

import statistics
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ...services.prediction_service import PredictionService, PredictionResult
from ...models.quiz import UserPrediction

router = APIRouter(prefix="/predictions", tags=["predictions"])


class PredictionRequest(BaseModel):
    """Request model for generating predictions."""
    user_id: str = Field(..., description="User ID")
    target_exam: str = Field(..., description="Target exam (e.g., 'CAT 2025')")
    quiz_session_id: Optional[str] = Field(None, description="Specific session to base prediction on")


class PredictionResponse(BaseModel):
    """Response model for prediction results."""
    predicted_rank: int = Field(..., description="Predicted overall rank")
    predicted_percentile: float = Field(..., description="Predicted overall percentile")
    subject_percentiles: dict = Field(..., description="Subject-wise percentiles")
    confidence_score: float = Field(..., description="Confidence in prediction (0-1)")
    improvement_suggestions: List[str] = Field(..., description="Personalized improvement suggestions")
    performance_trend: str = Field(..., description="Performance trend (improving/stable/declining)")
    expected_score_range: dict = Field(..., description="Expected score range")
    prediction_date: str = Field(..., description="Date when prediction was generated")


class SubjectAnalysisResponse(BaseModel):
    """Response model for subject-wise analysis."""
    subject: str
    current_percentile: float
    predicted_percentile: float
    strength_level: str  # "strong", "moderate", "weak"
    accuracy_trend: str  # "improving", "stable", "declining"
    recommendations: List[str]


class LeaderboardEntry(BaseModel):
    """Leaderboard entry with predictions."""
    user_id: str
    user_name: str
    predicted_rank: int
    predicted_percentile: float
    mock_tests_taken: int
    confidence_score: float


prediction_service = PredictionService()


@router.post("/generate", response_model=PredictionResponse)
async def generate_prediction(request: PredictionRequest):
    """
    Generate comprehensive prediction for a user's performance in target exam.
    
    This endpoint analyzes the user's mock test history and generates:
    - Predicted overall rank
    - Predicted overall percentile  
    - Subject-wise percentile predictions
    - Improvement suggestions
    - Performance trends
    """
    try:
        prediction = await prediction_service.generate_prediction(
            user_id=request.user_id,
            target_exam=request.target_exam,
            quiz_session_id=request.quiz_session_id
        )
        
        # Save prediction to database
        if request.quiz_session_id:
            await prediction_service.save_prediction(
                user_id=request.user_id,
                quiz_session_id=request.quiz_session_id,
                prediction=prediction,
                target_exam=request.target_exam
            )
        
        return PredictionResponse(
            predicted_rank=prediction.predicted_rank,
            predicted_percentile=prediction.predicted_percentile,
            subject_percentiles=prediction.subject_percentiles,
            confidence_score=prediction.confidence_score,
            improvement_suggestions=prediction.improvement_suggestions,
            performance_trend=prediction.performance_trend,
            expected_score_range=prediction.expected_score_range,
            prediction_date=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate prediction: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=List[PredictionResponse])
async def get_user_predictions(
    user_id: str,
    target_exam: str = Query(..., description="Target exam name"),
    limit: int = Query(10, description="Maximum number of predictions to return")
):
    """
    Get prediction history for a specific user.
    
    Returns the user's prediction history for the specified target exam,
    showing how their predicted performance has evolved over time.
    """
    try:
        predictions = await prediction_service.get_user_prediction_history(
            user_id=user_id,
            target_exam=target_exam
        )
        
        # Limit results
        predictions = predictions[:limit]
        
        response = []
        for pred in predictions:
            response.append(PredictionResponse(
                predicted_rank=pred.predicted_rank,
                predicted_percentile=pred.predicted_percentile,
                subject_percentiles=pred.subject_percentiles,
                confidence_score=pred.percentile_confidence,
                improvement_suggestions=pred.improvement_suggestions,
                performance_trend=pred.performance_trend,
                expected_score_range=pred.expected_score_range,
                prediction_date=pred.created_at.isoformat()
            ))
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user predictions: {str(e)}"
        )


@router.get("/subject-analysis/{user_id}", response_model=List[SubjectAnalysisResponse])
async def get_subject_analysis(
    user_id: str,
    target_exam: str = Query(..., description="Target exam name")
):
    """
    Get detailed subject-wise analysis and predictions for a user.
    
    Provides in-depth analysis of each subject including:
    - Current performance level
    - Predicted performance
    - Strength assessment
    - Improvement recommendations
    """
    try:
        prediction = await prediction_service.generate_prediction(
            user_id=user_id,
            target_exam=target_exam
        )
        
        # Get mock sessions for trend analysis
        mock_sessions = await prediction_service._get_user_mock_sessions(user_id, target_exam)
        
        subject_analyses = []
        
        for subject, predicted_percentile in prediction.subject_percentiles.items():
            # Calculate current performance
            recent_scores = []
            for session in mock_sessions[-3:]:  # Last 3 sessions
                if session.subject_scores and subject in session.subject_scores:
                    score_data = session.subject_scores[subject]
                    if isinstance(score_data, dict) and 'percentage' in score_data:
                        recent_scores.append(score_data['percentage'])
            
            current_percentile = statistics.mean(recent_scores) if recent_scores else 0
            
            # Determine strength level
            if predicted_percentile >= 80:
                strength_level = "strong"
            elif predicted_percentile >= 60:
                strength_level = "moderate"
            else:
                strength_level = "weak"
            
            # Determine trend
            if len(recent_scores) >= 2:
                if recent_scores[-1] > recent_scores[0] + 5:
                    trend = "improving"
                elif recent_scores[-1] < recent_scores[0] - 5:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "stable"
            
            # Generate recommendations
            recommendations = []
            if strength_level == "weak":
                recommendations.append(f"Focus on {subject} fundamentals")
                recommendations.append(f"Allocate more study time to {subject}")
            elif strength_level == "moderate":
                recommendations.append(f"Practice advanced {subject} problems")
                recommendations.append(f"Work on accuracy in {subject}")
            else:
                recommendations.append(f"Maintain current {subject} performance")
                recommendations.append(f"Focus on speed in {subject}")
            
            if trend == "declining":
                recommendations.append(f"Review recent {subject} mistakes")
            
            subject_analyses.append(SubjectAnalysisResponse(
                subject=subject,
                current_percentile=current_percentile,
                predicted_percentile=predicted_percentile,
                strength_level=strength_level,
                accuracy_trend=trend,
                recommendations=recommendations
            ))
        
        return subject_analyses
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get subject analysis: {str(e)}"
        )


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_prediction_leaderboard(
    target_exam: str = Query(..., description="Target exam name"),
    limit: int = Query(50, description="Number of entries to return")
):
    """
    Get leaderboard of predicted rankings for target exam.
    
    Shows the predicted rankings of all users who have taken sufficient
    mock tests, helping aspirants understand where they stand relative
    to other candidates.
    """
    try:
        # Get all recent predictions for target exam
        recent_predictions = await UserPrediction.find(
            UserPrediction.target_exam == target_exam,
            UserPrediction.percentile_confidence >= 0.5  # Only confident predictions
        ).sort(UserPrediction.predicted_rank).limit(limit).to_list()
        
        leaderboard = []
        
        for pred in recent_predictions:
            # Get user's mock test count
            mock_sessions = await prediction_service._get_user_mock_sessions(
                pred.user_id, target_exam
            )
            
            leaderboard.append(LeaderboardEntry(
                user_id=pred.user_id,
                user_name=f"User_{pred.user_id[:8]}",  # Anonymized
                predicted_rank=pred.predicted_rank,
                predicted_percentile=pred.predicted_percentile,
                mock_tests_taken=len(mock_sessions),
                confidence_score=pred.percentile_confidence
            ))
        
        return leaderboard
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get leaderboard: {str(e)}"
        )


@router.get("/analytics/{user_id}")
async def get_user_analytics(
    user_id: str,
    target_exam: str = Query(..., description="Target exam name")
):
    """
    Get comprehensive analytics for a user's mock test performance.
    
    Provides detailed insights including:
    - Performance trends over time
    - Subject-wise progress
    - Comparison with peer group
    - Areas for improvement
    """
    try:
        # Get user's prediction
        prediction = await prediction_service.generate_prediction(
            user_id=user_id,
            target_exam=target_exam
        )
        
        # Get mock sessions for trend analysis
        mock_sessions = await prediction_service._get_user_mock_sessions(user_id, target_exam)
        
        # Calculate additional analytics
        analytics = {
            "overview": {
                "total_mock_tests": len(mock_sessions),
                "predicted_rank": prediction.predicted_rank,
                "predicted_percentile": prediction.predicted_percentile,
                "confidence_score": prediction.confidence_score,
                "performance_trend": prediction.performance_trend
            },
            "subject_performance": prediction.subject_percentiles,
            "improvement_suggestions": prediction.improvement_suggestions,
            "expected_score_range": prediction.expected_score_range,
            "consistency_metrics": {
                "consistency_score": await prediction_service._calculate_consistency_score(mock_sessions),
                "time_efficiency": await prediction_service._calculate_time_efficiency(mock_sessions)
            },
            "progress_over_time": [
                {
                    "date": session.started_at.isoformat(),
                    "percentile": session.percentage_score,
                    "subjects": session.subject_scores
                }
                for session in mock_sessions[-10:]  # Last 10 sessions
            ]
        }
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user analytics: {str(e)}"
        )
