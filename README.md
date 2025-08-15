# MCQ Quiz Platform

A MCQ Quiz Platform built with FastAPI and MongoDB

## 🚀 Features

- **Clean Architecture**: Separation of concerns with models, repositories, services, and API layers
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Async/Await**: Full asynchronous support throughout the application
- **MongoDB**: NoSQL database with Beanie ODM for document modeling
- **Motor**: Async MongoDB driver for Python
- **Pydantic**: Data validation and serialization with type hints
- **JWT Authentication**: Secure token-based authentication
- **Comprehensive Testing**: Unit and integration tests with pytest-asyncio
- **CORS Support**: Configured for frontend integration (Lovable)
- **Code Quality**: Type hints and proper error handling
- **Configuration Management**: Environment-based settings with Pydantic

## 📁 Project Structure

```
src/
├── api/                    # API layer
│   ├── dependencies.py    # FastAPI dependencies
│   ├── schemas.py         # Pydantic schemas/DTOs
│   └── endpoints/         # API endpoints
│       ├── quiz.py        # Quiz CRUD operations
│       └── answer.py      # Answer submission and sessions
├── config/                # Configuration management
│   ├── database.py        # MongoDB configuration
│   └── settings.py        # Application settings
├── models/                # MongoDB document models
│   └── quiz.py           # Quiz, Question, Answer, Session models
├── repositories/          # Data access layer
│   └── quiz_repository.py # MongoDB operations and aggregations
├── services/              # Business logic layer
│   └── quiz_service.py    # Quiz, Answer, Session services
└── main.py               # FastAPI application entry point

tests/
├── conftest.py           # MongoDB test configuration and fixtures
└── unit/                 # Unit tests
    └── test_quiz_service.py
```
└── integration/          # Integration tests

docs/                     # Documentation
scripts/                  # Utility scripts
docker/                   # Docker configuration
```

## 🛠️ Setup

### Prerequisites

- Python 3.11+
- MongoDB Atlas account (or local MongoDB)
- Redis (for caching)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mcq-quiz-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB configuration
   ```

5. **Configure MongoDB**
   ```bash
   # Set up MongoDB Atlas connection string in .env
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority&appName=yourapp
   ```

### Development

1. **Start the development server**
   ```bash
   python -m src.main
   ```

2. **API Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Run tests**
   ```bash
   pytest
   ```

4. **Code formatting and linting**
   ```bash
   black src tests
   isort src tests
   flake8 src tests
   mypy src
   ```

## 🐳 Docker

### Development
```bash
docker-compose up --build
```

### Production
```bash
docker build -t python-boilerplate .
docker run -p 8000:8000 python-boilerplate
```

## 📊 Testing

The project includes comprehensive testing setup:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Test Coverage**: Minimum 80% coverage required
- **Fixtures**: Reusable test data and mock objects

Run tests with coverage:
```bash
pytest --cov=src --cov-report=html
```

## 🔧 Configuration

Configuration is managed through environment variables and Pydantic settings:

- **Database**: Connection string, pool settings
- **Redis**: Cache configuration  
- **JWT**: Secret keys, token expiration
- **CORS**: Allowed origins, methods, headers
- **Logging**: Level, format
- **External APIs**: Base URLs, API keys

## 🔒 Security

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt for password security
- **Input Validation**: Pydantic for request validation
- **CORS**: Configurable cross-origin requests
- **SQL Injection Protection**: SQLAlchemy ORM

## 📈 Monitoring

- **Structured Logging**: JSON formatted logs with structlog
- **Health Checks**: Built-in health check endpoint
- **Error Tracking**: Sentry integration (optional)
- **Metrics**: Application performance metrics

## 🚀 Deployment

### Environment Variables

Required environment variables for production:

```bash
# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-production-secret-key

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Redis
REDIS_URL=redis://host:6379/0

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### Production Checklist

- [ ] Set strong SECRET_KEY
- [ ] Configure production database
- [ ] Set up Redis for caching
- [ ] Configure CORS for your domain
- [ ] Set up monitoring and logging
- [ ] Configure SSL/TLS
- [ ] Set up backup strategy
- [ ] Configure rate limiting
- [ ] Review security settings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Documentation: `/docs` endpoint when running
- Issues: GitHub Issues
- Discussions: GitHub Discussions

## 🎯 Roadmap

- [ ] GraphQL support
- [ ] WebSocket support
- [ ] Background task queue
- [ ] API rate limiting
- [ ] Advanced caching strategies
- [ ] Microservices support
- [ ] Kubernetes deployment configs
