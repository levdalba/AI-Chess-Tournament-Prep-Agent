# AI Chess Tournament Prep Agent 🏆♟️

An intelligent chess tournament preparation system that analyzes opponents and creates personalized training plans using AI.

## 🎯 Project Vision

This application helps chess players prepare for tournaments by:

-   Analyzing opponents' games from Chess.com, Lichess, and FIDE databases
-   Identifying patterns, strengths, and weaknesses
-   Generating AI-powered preparation plans with daily training schedules
-   Creating targeted opening repertoires and tactical training

## �️ Architecture Overview

```
chess-tournament-prep/
├── frontend/          # React + TypeScript + Vite
├── backend/           # FastAPI + Python
├── data/              # Chess data fetchers and analyzers
├── ai/                # AI service (Grok integration)
├── database/          # PostgreSQL schemas and migrations
├── services/          # Background services (Celery)
├── shared/            # Common models and utilities
├── infrastructure/    # Docker, deployment configs
├── tests/             # Test suites
└── docs/              # Documentation
```

## 🚀 Getting Started

### Prerequisites

-   Python 3.11+
-   Node.js 18+
-   Docker and Docker Compose
-   PostgreSQL
-   Redis
-   Stockfish chess engine

### Quick Start with Docker

```bash
# Clone the repository
git clone <repository-url>
cd ai-chess-tournament-prep-agent

# Copy environment template and configure
cp .env.template .env
# Edit .env with your configuration (API keys, database settings, etc.)

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

## 🔧 Development Setup

### 1. Install Dependencies

```bash
# Install Python dependencies for data analysis
cd data && pip install -r requirements.txt

# Install AI service dependencies
cd ../ai && pip install -r requirements.txt

# Install backend dependencies
cd ../backend && pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend && npm install
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your settings:
# - Add your Grok API key from xAI
# - Configure database connection
# - Set Stockfish path
# - Configure other API keys
```

### 3. Database Setup

```bash
# Start PostgreSQL (via Docker)
docker run --name chess-postgres -e POSTGRES_USER=chess_user -e POSTGRES_PASSWORD=chess_pass -e POSTGRES_DB=chess_prep_db -p 5432:5432 -d postgres:15

# Initialize database
cd backend
python -m database init
```

### 4. Start Services

```bash
# Terminal 1: Start backend server
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend dev server
cd frontend
npm run dev

# Terminal 3: Start Redis for caching (optional)
docker run --name chess-redis -p 6379:6379 -d redis:7-alpine
```

### 5. Install Chess Engine

```bash
# macOS with Homebrew
brew install stockfish

# Ubuntu/Debian
sudo apt install stockfish

# Or download from: https://stockfishchess.org/download/
```

## 📊 Features

### ✅ Implemented Features

-   **Multi-platform Data Fetching**: Chess.com, Lichess, FIDE/TWIC archives
-   **Chess Engine Analysis**: Stockfish integration for game analysis
-   **Opening Analysis**: Comprehensive repertoire analysis and statistics
-   **Weakness Detection**: Identify tactical and strategic weaknesses by game phase
-   **AI Preparation Plans**: Grok-powered personalized training plans
-   **Modern Frontend**: React 18 + TypeScript + Tailwind CSS
-   **RESTful API**: FastAPI with automatic documentation
-   **Database Integration**: PostgreSQL with SQLAlchemy ORM
-   **Authentication System**: JWT-based user authentication

### 🔄 In Progress Features

-   Background task processing with Celery
-   Advanced statistical analysis and visualizations
-   Tournament scheduling integration
-   Email notifications for prep reminders

### 📋 Planned Features

-   Real-time game analysis during play
-   Collaborative prep planning with coaches
-   Mobile app (React Native)
-   Integration with more chess platforms
-   Advanced AI coaching feedback

## 🛠️ Tech Stack

### Frontend

-   **Framework**: React 18 with TypeScript
-   **Build Tool**: Vite 5
-   **Styling**: Tailwind CSS v3.4
-   **State Management**: React Query (TanStack Query v5)
-   **Routing**: React Router v6
-   **HTTP Client**: Axios with interceptors
-   **UI Components**: Custom component library

### Backend

-   **Framework**: FastAPI 0.104+
-   **Database**: PostgreSQL 15 with AsyncPG
-   **ORM**: SQLAlchemy 2.0 with async support
-   **Authentication**: JWT with PassLib + bcrypt
-   **Background Tasks**: Celery + Redis
-   **Chess Analysis**: python-chess + Stockfish
-   **Data Fetching**: aiohttp + BeautifulSoup4
-   **Validation**: Pydantic v2

### AI & Analysis Engine

-   **AI Model**: xAI Grok Beta API
-   **Chess Engine**: Stockfish 15+
-   **Analysis Libraries**: python-chess for game processing
-   **Data Sources**:
    -   Chess.com Public API
    -   Lichess Streaming API
    -   The Week in Chess (TWIC) Archives
    -   FIDE tournament databases

### Infrastructure & DevOps

-   **Containerization**: Docker + Docker Compose
-   **Database**: PostgreSQL 15
-   **Cache/Message Broker**: Redis 7
-   **Web Server**: Uvicorn with Gunicorn
-   **Reverse Proxy**: Nginx (production)
-   **Process Management**: Supervisor

## � API Documentation

Interactive API documentation is available at:

-   **Swagger UI**: `http://localhost:8000/docs`
-   **ReDoc**: `http://localhost:8000/redoc`

### Core Endpoints

#### Authentication

```http
POST /auth/login - User login
POST /auth/register - User registration
```

#### Player Analysis

```http
POST /api/players/search - Search player and fetch games
POST /api/analysis/player - Comprehensive player analysis
GET /api/players/{player_id}/games - Get player's games
GET /api/players/{player_id}/repertoire - Get opening repertoire
```

#### AI Preparation

```http
POST /api/analysis/prep-plan - Generate AI preparation plan
POST /api/prep-plans/{plan_id}/exercises - Get daily exercises
GET /api/prep-plans/{plan_id} - Get preparation plan details
PUT /api/prep-plans/{plan_id}/progress - Update training progress
```

#### Dashboard

```http
GET /api/dashboard/stats - User dashboard statistics
GET /api/dashboard/recent-games - Recent analyzed games
GET /api/dashboard/upcoming-tournaments - Upcoming tournaments
```

## 🗄️ Database Schema

### Core Tables

-   **users** - User accounts and preferences
-   **player_profiles** - Chess platform profiles (Chess.com, Lichess, FIDE)
-   **chess_games** - Game records with PGN data and metadata
-   **game_analyses** - Stockfish analysis results
-   **opening_repertoires** - Opening statistics and preferences
-   **player_analyses** - Comprehensive analysis results
-   **prep_plans** - AI-generated preparation plans
-   **training_sessions** - Daily training session tracking
-   **tournaments** - Tournament information and scheduling

### Relationships

```sql
users (1:N) player_profiles (1:N) chess_games (1:1) game_analyses
users (1:N) player_analyses (1:N) prep_plans (1:N) training_sessions
player_profiles (1:1) opening_repertoires
```

## 🤖 AI Integration

### Grok API Integration

The system uses xAI's Grok API for intelligent preparation planning:

```python
# Generate preparation plan
async with GrokAIService(api_key) as ai:
    prep_plan = await ai.generate_prep_plan(
        player_analysis=player_data,
        opponent_analysis=opponent_data,
        tournament_info=tournament_details
    )
```

### AI-Generated Content

-   **Opening Preparation**: Specific variations to study against opponent
-   **Tactical Themes**: Weakness-based tactical patterns to practice
-   **Strategic Focus**: Key strategic concepts for the matchup
-   **Daily Training Plans**: Structured 7-14 day preparation schedules
-   **Psychological Notes**: Mental preparation and confidence building
-   **Time Management**: Clock management strategies per game phase

## 📊 Data Sources & Analysis

### Chess.com API

-   Monthly game archives (PGN format)
-   Player ratings and statistics
-   Tournament participation data
-   Rate limited: 300 requests/day

### Lichess API

-   Real-time game streaming
-   Player activity and preferences
-   Tournament results
-   Open API with higher rate limits

### FIDE/TWIC Integration

-   Official tournament games (PGN)
-   Classical time control focus
-   Grandmaster and titled player games
-   Weekly archive processing

### Analysis Pipeline

1. **Data Fetching**: Async fetching from multiple sources
2. **Game Parsing**: PGN processing with python-chess
3. **Engine Analysis**: Stockfish evaluation (1-15 depth)
4. **Pattern Recognition**: Opening classification and weakness detection
5. **Statistical Analysis**: Performance metrics and trends
6. **AI Processing**: Grok API for strategic insights

## 🔐 Security & Performance

### Security Features

-   **Authentication**: JWT tokens with refresh mechanism
-   **Password Security**: bcrypt hashing with salt
-   **API Security**: Rate limiting and CORS protection
-   **Input Validation**: Pydantic model validation
-   **SQL Security**: SQLAlchemy ORM prevents injection attacks
-   **Environment Security**: Secrets management with env files

### Performance Optimizations

-   **Async Architecture**: Full async/await implementation
-   **Connection Pooling**: Database connection pooling with AsyncPG
-   **Caching Strategy**: Redis caching for expensive operations
-   **Background Processing**: Celery for long-running analysis tasks
-   **Database Indexing**: Optimized queries with proper indexing
-   **API Response Optimization**: Paginated responses and field selection

## 🧪 Testing Strategy

### Backend Testing

```bash
cd backend
pytest tests/ -v --cov=. --cov-report=html
```

### Frontend Testing

```bash
cd frontend
npm test -- --coverage
npm run test:e2e
```

### Integration Testing

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Test Coverage Areas

-   Unit tests for data fetchers and analyzers
-   API endpoint testing with test database
-   Frontend component testing with React Testing Library
-   Integration tests for full user workflows
-   Performance testing for analysis operations

## � Deployment

### Production Docker Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with environment variables
export GROK_API_KEY="your-key"
export DATABASE_URL="postgresql://..."
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Configuration

Required environment variables:

```bash
# Core API Keys
GROK_API_KEY=xai-grok-api-key
CHESS_COM_API_KEY=optional-chess-com-key

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
REDIS_URL=redis://host:port/db

# Security
SECRET_KEY=your-secret-key-256-bits
JWT_ALGORITHM=HS256

# Chess Engine
STOCKFISH_PATH=/usr/local/bin/stockfish

# Performance
CELERY_BROKER_URL=redis://host:port/1
RATE_LIMIT_PER_MINUTE=60
```

### Production Checklist

-   [ ] Environment variables configured
-   [ ] Database migrations applied
-   [ ] Redis server running
-   [ ] Stockfish engine installed
-   [ ] SSL certificates configured
-   [ ] Monitoring and logging setup
-   [ ] Backup strategy implemented
-   [ ] Load balancing configured

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork & Clone**

    ```bash
    git clone https://github.com/your-username/ai-chess-tournament-prep-agent
    cd ai-chess-tournament-prep-agent
    ```

2. **Create Feature Branch**

    ```bash
    git checkout -b feature/awesome-feature
    ```

3. **Set Up Development Environment**

    ```bash
    cp .env.template .env
    # Configure your development environment
    ```

4. **Make Changes & Test**

    ```bash
    # Run tests before committing
    pytest backend/tests/
    npm test --prefix frontend/
    ```

5. **Commit & Push**

    ```bash
    git commit -m "feat: add awesome feature"
    git push origin feature/awesome-feature
    ```

6. **Open Pull Request**
    - Use conventional commit messages
    - Include tests for new features
    - Update documentation as needed

### Development Guidelines

-   Follow PEP 8 for Python code
-   Use TypeScript strict mode for frontend
-   Write comprehensive tests
-   Document API changes
-   Use semantic versioning

## � License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

-   **Chess Libraries**: [python-chess](https://python-chess.readthedocs.io/) for game processing
-   **Chess Engine**: [Stockfish](https://stockfishchess.org/) for position analysis
-   **Data Sources**: [Chess.com](https://chess.com), [Lichess](https://lichess.org), [TWIC](https://theweekinchess.com)
-   **AI Platform**: [xAI Grok](https://x.ai/) for intelligent preparation planning
-   **Web Frameworks**: FastAPI and React ecosystems
-   **Chess Community**: For inspiration and feedback

---

**Built with ❤️ for chess players who want to level up their tournament preparation**

_Ready to dominate your next tournament? Let AI be your secret weapon! 🚀_
