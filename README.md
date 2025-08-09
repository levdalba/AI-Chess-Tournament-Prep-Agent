# AI Chess Tournament Prep Agent

🏆 **Professional chess preparation powered by AI**

An intelligent agent that analyzes opponents' games, identifies weaknesses, and creates personalized tournament preparation plans with daily training drills.

## 🎯 Features

- **PGN Analysis**: Upload and analyze opponents' games from Lichess/Chess.com
- **Opening Detection**: Identify common opening patterns and variations
- **Weakness Analysis**: Find tactical and positional weak points using Stockfish
- **AI-Powered Prep Plans**: Generate custom preparation strategies using Grok AI
- **Daily Drills**: Automated delivery of personalized training exercises
- **Progress Tracking**: Monitor improvement and preparation progress

## 🏗️ Architecture

This project follows a modern microservices architecture:

- **Frontend**: React.js with TypeScript
- **Backend**: FastAPI with Python
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Integration**: xAI Grok API
- **Chess Engine**: Stockfish integration
- **Background Tasks**: Celery with Redis
- **Containerization**: Docker & Docker Compose

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/levdalba/AI-Chess-Tournament-Prep-Agent.git
cd AI-Chess-Tournament-Prep-Agent

# Start with Docker Compose
docker-compose up -d

# Or run manually (see docs/setup.md for detailed instructions)
```

## 📁 Project Structure

```
├── frontend/          # React.js client application
├── backend/           # FastAPI server
├── data/              # Chess analysis & data processing
├── ai/                # AI/ML services
├── database/          # Database models & migrations
├── services/          # External integrations
├── shared/            # Shared utilities
├── infrastructure/    # Deployment & containerization
├── tests/             # Test suites
└── docs/              # Documentation
```

## 🎯 Target Users

- Competitive chess players
- Chess coaches and trainers
- Chess clubs and organizations

## 📈 Development Roadmap

- [x] Project setup and architecture
- [ ] Frontend development
- [ ] Backend API development
- [ ] Chess analysis engine
- [ ] AI integration
- [ ] User authentication
- [ ] Daily drill system
- [ ] Deployment pipeline

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.
