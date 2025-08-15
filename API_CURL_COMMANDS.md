# MCQ Quiz Platform - Complete API Reference with cURL Commands

## Base URL
```
http://localhost:8000
```

## Headers
All requests should include:
```
Content-Type: application/json
user-id: your-user-id-here
```

---

## 🎯 Quiz Management Endpoints

### 1. Create Quiz
```bash
curl -X POST "http://localhost:8000/api/v1/quiz/quizzes" \
  -H "Content-Type: application/json" \
  -H "user-id: user-123" \
  -d '{
    "title": "JavaScript Fundamentals",
    "description": "Test your knowledge of JavaScript basics",
    "difficulty": "medium",
    "time_limit_minutes": 30,
    "passing_score": 70,
    "is_active": true,
    "category": "Programming"
  }'
```

### 2. Get All Quizzes
```bash
curl -X GET "http://localhost:8000/api/v1/quiz/quizzes" \
  -H "user-id: user-123"
```

### 3. Get All Quizzes with Filters
```bash
curl -X GET "http://localhost:8000/api/v1/quiz/quizzes?difficulty=medium&category=Programming&is_active=true&skip=0&limit=10" \
  -H "user-id: user-123"
```

### 4. Get Specific Quiz
```bash
curl -X GET "http://localhost:8000/api/v1/quiz/quizzes/quiz-id-here" \
  -H "user-id: user-123"
```

### 5. Update Quiz
```bash
curl -X PUT "http://localhost:8000/api/v1/quiz/quizzes/quiz-id-here" \
  -H "Content-Type: application/json" \
  -H "user-id: user-123" \
  -d '{
    "title": "Advanced JavaScript",
    "description": "Updated description",
    "difficulty": "hard",
    "time_limit_minutes": 45,
    "passing_score": 80
  }'
```

### 6. Delete Quiz
```bash
curl -X DELETE "http://localhost:8000/api/v1/quiz/quizzes/quiz-id-here" \
  -H "user-id: user-123"
```

---

## 📝 Question Management Endpoints

### 7. Create Single Question
```bash
curl -X POST "http://localhost:8000/api/v1/quiz/questions" \
  -H "Content-Type: application/json" \
  -H "user-id: user-123" \
  -d '{
    "quiz_id": "quiz-id-here",
    "question_text": "What is the correct way to declare a variable in JavaScript?",
    "question_type": "single_choice",
    "options": [
      "var myVar = 5;",
      "variable myVar = 5;",
      "v myVar = 5;",
      "declare myVar = 5;"
    ],
    "correct_answers": ["var myVar = 5;"],
    "explanation": "In JavaScript, variables are declared using var, let, or const keywords.",
    "points": 10,
    "difficulty": "easy",
    "order_index": 1
  }'
```

### 8. Create Multiple Questions (Bulk)
```bash
curl -X POST "http://localhost:8000/api/v1/quiz/questions/bulk" \
  -H "Content-Type: application/json" \
  -H "user-id: user-123" \
  -d '{
    "questions": [
      {
        "quiz_id": "quiz-id-here",
        "question_text": "Which of the following are JavaScript data types?",
        "question_type": "multiple_choice",
        "options": ["String", "Number", "Boolean", "Character"],
        "correct_answers": ["String", "Number", "Boolean"],
        "explanation": "JavaScript has String, Number, Boolean, Object, and other types, but not Character.",
        "points": 15,
        "difficulty": "medium",
        "order_index": 2
      },
      {
        "quiz_id": "quiz-id-here",
        "question_text": "What does DOM stand for?",
        "question_type": "single_choice",
        "options": ["Document Object Model", "Data Object Management", "Dynamic Object Method", "Document Oriented Model"],
        "correct_answers": ["Document Object Model"],
        "explanation": "DOM stands for Document Object Model.",
        "points": 5,
        "difficulty": "easy",
        "order_index": 3
      }
    ]
  }'
```

### 9. Get Questions for a Quiz (Public - for quiz takers)
```bash
curl -X GET "http://localhost:8000/api/v1/quiz/quizzes/quiz-id-here/questions" \
  -H "user-id: user-123"
```

### 10. Get Questions with Randomization
```bash
curl -X GET "http://localhost:8000/api/v1/quiz/quizzes/quiz-id-here/questions?randomize=true&limit=5" \
  -H "user-id: user-123"
```

### 11. Get Specific Question (Admin - includes correct answers)
```bash
curl -X GET "http://localhost:8000/api/v1/quiz/questions/question-id-here" \
  -H "user-id: user-123"
```

### 12. Update Question
```bash
curl -X PUT "http://localhost:8000/api/v1/quiz/questions/question-id-here" \
  -H "Content-Type: application/json" \
  -H "user-id: user-123" \
  -d '{
    "question_text": "Updated: What is the correct way to declare a variable in JavaScript?",
    "options": [
      "let myVar = 5;",
      "var myVar = 5;", 
      "const myVar = 5;",
      "variable myVar = 5;"
    ],
    "correct_answers": ["let myVar = 5;", "var myVar = 5;", "const myVar = 5;"],
    "explanation": "Variables can be declared using let, var, or const keywords.",
    "points": 12
  }'
```

### 13. Delete Question
```bash
curl -X DELETE "http://localhost:8000/api/v1/quiz/questions/question-id-here" \
  -H "user-id: user-123"
```

---

## 🎮 Quiz Interaction Endpoints (Main Platform Features)

### 14. Get Available Questions (Main Endpoint)
```bash
curl -X GET "http://localhost:8000/api/v1/get-questions" \
  -H "user-id: user-123"
```

### 15. Get Questions with Filters
```bash
curl -X GET "http://localhost:8000/api/v1/get-questions?quiz_id=quiz-id-here&difficulty=medium&limit=10&randomize=true" \
  -H "user-id: user-123"
```

### 16. Get Specific Question by ID (Main Endpoint)
```bash
curl -X GET "http://localhost:8000/api/v1/get-questions-by-id/question-id-here" \
  -H "user-id: user-123"
```

### 17. Submit Answer (Main Endpoint)
```bash
curl -X POST "http://localhost:8000/api/v1/submit-answer" \
  -H "Content-Type: application/json" \
  -H "user-id: user-123" \
  -d '{
    "question_id": "question-id-here",
    "session_id": "session-id-here",
    "selected_answers": ["var myVar = 5;"],
    "time_taken_seconds": 15
  }'
```

### 18. Submit Multiple Choice Answer
```bash
curl -X POST "http://localhost:8000/api/v1/submit-answer" \
  -H "Content-Type: application/json" \
  -H "user-id: user-123" \
  -d '{
    "question_id": "question-id-here",
    "session_id": "session-id-here", 
    "selected_answers": ["String", "Number", "Boolean"],
    "time_taken_seconds": 25
  }'
```

---

## 🏁 Quiz Session Management

### 19. Start Quiz Session
```bash
curl -X POST "http://localhost:8000/api/v1/quiz-sessions/start" \
  -H "Content-Type: application/json" \
  -H "user-id: user-123" \
  -d '{
    "quiz_id": "quiz-id-here"
  }'
```

### 20. Get Session Details
```bash
curl -X GET "http://localhost:8000/api/v1/quiz-sessions/session-id-here" \
  -H "user-id: user-123"
```

### 21. Complete Quiz Session
```bash
curl -X POST "http://localhost:8000/api/v1/quiz-sessions/session-id-here/complete" \
  -H "user-id: user-123"
```

### 22. Abandon Quiz Session
```bash
curl -X POST "http://localhost:8000/api/v1/quiz-sessions/session-id-here/abandon" \
  -H "user-id: user-123"
```

---

## 📊 Statistics and Leaderboards

### 23. Get Quiz Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/quizzes/quiz-id-here/statistics" \
  -H "user-id: user-123"
```

### 24. Get Quiz Leaderboard
```bash
curl -X GET "http://localhost:8000/api/v1/quizzes/quiz-id-here/leaderboard" \
  -H "user-id: user-123"
```

### 25. Get Leaderboard with Limit
```bash
curl -X GET "http://localhost:8000/api/v1/quizzes/quiz-id-here/leaderboard?limit=10" \
  -H "user-id: user-123"
```

---

## 📋 API Documentation

### 26. Get API Documentation
```bash
curl -X GET "http://localhost:8000/docs"
```

### 27. Get OpenAPI Schema
```bash
curl -X GET "http://localhost:8000/openapi.json"
```

---

## 🔄 Complete Quiz Flow Example

### Step 1: Create a Quiz
```bash
QUIZ_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/quiz/quizzes" \
  -H "Content-Type: application/json" \
  -H "user-id: user-123" \
  -d '{
    "title": "JavaScript Basics",
    "description": "Test your JavaScript knowledge",
    "difficulty": "medium",
    "time_limit_minutes": 30,
    "passing_score": 70,
    "is_active": true
  }')

QUIZ_ID=$(echo $QUIZ_RESPONSE | jq -r '.id')
```

### Step 2: Add Questions
```bash
curl -X POST "http://localhost:8000/api/v1/quiz/questions/bulk" \
  -H "Content-Type: application/json" \
  -H "user-id: user-123" \
  -d "{
    \"questions\": [
      {
        \"quiz_id\": \"$QUIZ_ID\",
        \"question_text\": \"What is JavaScript?\",
        \"question_type\": \"single_choice\",
        \"options\": [\"Programming Language\", \"Markup Language\", \"Database\", \"Framework\"],
        \"correct_answers\": [\"Programming Language\"],
        \"explanation\": \"JavaScript is a programming language.\",
        \"points\": 10,
        \"order_index\": 1
      }
    ]
  }"
```

### Step 3: Start Quiz Session
```bash
SESSION_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/quiz-sessions/start" \
  -H "Content-Type: application/json" \
  -H "user-id: user-123" \
  -d "{\"quiz_id\": \"$QUIZ_ID\"}")

SESSION_ID=$(echo $SESSION_RESPONSE | jq -r '.id')
```

### Step 4: Get Questions
```bash
curl -X GET "http://localhost:8000/api/v1/get-questions?quiz_id=$QUIZ_ID" \
  -H "user-id: user-123"
```

### Step 5: Submit Answers
```bash
curl -X POST "http://localhost:8000/api/v1/submit-answer" \
  -H "Content-Type: application/json" \
  -H "user-id: user-123" \
  -d "{
    \"question_id\": \"question-id-here\",
    \"session_id\": \"$SESSION_ID\",
    \"selected_answers\": [\"Programming Language\"],
    \"time_taken_seconds\": 10
  }"
```

### Step 6: Complete Session
```bash
curl -X POST "http://localhost:8000/api/v1/quiz-sessions/$SESSION_ID/complete" \
  -H "user-id: user-123"
```

---

## 🏷️ Response Examples

### Quiz Response
```json
{
  "id": "quiz-uuid-here",
  "title": "JavaScript Fundamentals",
  "description": "Test your knowledge of JavaScript basics",
  "difficulty": "medium",
  "time_limit_minutes": 30,
  "passing_score": 70,
  "is_active": true,
  "category": "Programming",
  "created_at": "2025-08-12T10:30:00",
  "question_count": 5
}
```

### Question Response (Public)
```json
{
  "id": "question-uuid-here",
  "quiz_id": "quiz-uuid-here",
  "question_text": "What is the correct way to declare a variable in JavaScript?",
  "question_type": "single_choice",
  "options": ["var myVar = 5;", "variable myVar = 5;", "v myVar = 5;", "declare myVar = 5;"],
  "points": 10,
  "difficulty": "easy",
  "order_index": 1
}
```

### Answer Submission Response
```json
{
  "id": "answer-uuid-here",
  "question_id": "question-uuid-here",
  "session_id": "session-uuid-here",
  "selected_answers": ["var myVar = 5;"],
  "is_correct": true,
  "points_earned": 10,
  "time_taken_seconds": 15,
  "created_at": "2025-08-12T10:35:00"
}
```

### Session Response
```json
{
  "id": "session-uuid-here",
  "quiz_id": "quiz-uuid-here",
  "user_id": "user-123",
  "status": "in_progress",
  "score": 25,
  "total_possible_score": 50,
  "questions_answered": 2,
  "total_questions": 5,
  "time_elapsed_seconds": 120,
  "started_at": "2025-08-12T10:30:00",
  "completed_at": null
}
```

---

## 🚀 Frontend Development Notes

### Key Frontend Features to Implement:
1. **Quiz Dashboard**: List all available quizzes with filters
2. **Quiz Taking Interface**: Question display with timer and answer submission
3. **Session Management**: Start, pause, resume, and complete quiz sessions
4. **Progress Tracking**: Real-time score and progress updates
5. **Results Display**: Show scores, correct answers, and explanations
6. **Leaderboards**: Display rankings and statistics
7. **Admin Panel**: Create and manage quizzes and questions

### Authentication:
- Use `user-id` header for user identification
- Ready for JWT token integration in headers

### Real-time Features:
- Consider WebSocket integration for real-time quiz updates
- Timer synchronization for timed quizzes
- Live leaderboard updates

### Error Handling:
- All endpoints return structured error responses
- Handle 404 for not found resources
- Handle 422 for validation errors

This complete API reference provides all the curl commands needed to build a comprehensive MCQ Quiz Platform frontend!
