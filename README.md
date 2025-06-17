# Homework Management System API

FastAPI backend for educational homework management system with AI grading integration using DeepSeek v3. Supports admin/teacher/student roles with device session management, homework submission, and AI-powered grading.

## 🚀 Features

- **Role-based Access Control**: Admin, Teacher, and Student roles
- **AI-Powered Grading**: Integration with DeepSeek v3 for automatic code grading
- **Device Session Management**: Max 3 active sessions per user
- **Homework Management**: Create, assign, and track homework submissions
- **Real-time Leaderboards**: Track student performance over time
- **File Upload Support**: Multiple programming languages supported
- **Grade Override**: Teachers can modify AI grades
- **Secure Authentication**: JWT tokens with bcrypt password hashing

## 🛠️ Technology Stack

- **Backend**: FastAPI + SQLAlchemy
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT tokens
- **AI Integration**: DeepSeek v3 API
- **Password Hashing**: bcrypt

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd homework_api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Configure DeepSeek API**
   - Get your API key from [DeepSeek](https://api.deepseek.com)
   - Add it to your `.env` file:
   ```
   DEEPSEEK_API_KEY=your-api-key-here
   ```

6. **Initialize database**
   ```bash
   python init_db.py
   ```

7. **Start the server**
   ```bash
   python run.py
   ```

## ⚙️ Configuration

Edit the `.env` file:

```env
# Database
DATABASE_URL=sqlite:///./homework.db

# Security
SECRET_KEY=your-secret-key-change-this-in-production

# DeepSeek AI
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions

# Server (optional)
HOST=127.0.0.1
PORT=8000
RELOAD=true
```

## 👥 Default Users

After running `init_db.py`, you'll have these test accounts:

| Role | Username | Password | Description |
|------|----------|----------|-------------|
| Admin | `admin` | `admin123` | System administrator |
| Teacher | `teacher1` | `teacher123` | Sample teacher |
| Student | `alice` | `student123` | Sample student 1 |
| Student | `bob` | `student123` | Sample student 2 |
| Student | `charlie` | `student123` | Sample student 3 |

**⚠️ Change these passwords in production!**

## 📚 API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 API Endpoints

### Authentication (`/auth`)
- `POST /auth/login` - Login with device management
- `POST /auth/login/force` - Force login by kicking out a device
- `POST /auth/logout` - Logout current session
- `GET /auth/sessions` - Get active sessions
- `DELETE /auth/sessions/{session_id}` - Remove specific session

### Constants (`/app`)
- `GET /app/constants` - Get system constants

### Admin (`/admin`) - Admin only
- **Teachers**: CRUD operations for teachers
- **Students**: CRUD operations for students  
- **Groups**: CRUD operations for groups
- **Management**: Assign students to groups, teachers to groups
- **Analytics**: View any group's leaderboard

### Teacher (`/teacher`) - Teachers only
- **Homework**: Create, update, delete homework
- **Groups**: View assigned groups
- **Submissions**: View and grade student submissions
- **Leaderboards**: View group performance

### Student (`/student`) - Students only
- **Homework**: View available homework
- **Submissions**: Submit homework and view history
- **Grades**: View detailed grade breakdowns
- **Leaderboard**: View group rankings

## 🎯 Usage Examples

### 1. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teacher1",
    "password": "teacher123", 
    "device_name": "My Laptop"
  }'
```

### 2. Create Homework (Teacher)
```bash
curl -X POST "http://localhost:8000/teacher/homework" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics",
    "description": "Write a function to calculate fibonacci numbers",
    "points": 100,
    "start_date": "2025-06-16T00:00:00",
    "deadline": "2025-06-23T23:59:59",
    "line_limit": 300,
    "file_extension": ".py",
    "group_id": 1,
    "ai_grading_prompt": "Check code correctness, efficiency, and style"
  }'
```

### 3. Submit Homework (Student)
```bash
curl -X POST "http://localhost:8000/student/homework/1/submit" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      {
        "file_name": "fibonacci.py",
        "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
      }
    ]
  }'
```

## 🤖 AI Grading

The system uses DeepSeek v3 to automatically grade submissions based on:

1. **Task Completeness** (0-100): How well the code fulfills requirements
2. **Code Quality** (0-100): Code structure, readability, best practices  
3. **Correctness** (0-100): Does the code work correctly and handle edge cases

Teachers can override AI grades and provide additional feedback.

## 🏆 Leaderboard System

Leaderboards track student performance with filtering options:
- **Day**: Today's submissions only
- **Week**: Current week (Monday-Sunday)
- **Month**: Current month
- **All**: All-time performance

Rankings are based on total points earned from homework submissions.

## 🔒 Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Authentication**: Secure token-based auth
- **Session Management**: Max 3 devices per user
- **Role-based Access**: Strict permission checking
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy ORM

## 🚀 Deployment

For production deployment:

1. **Use PostgreSQL**:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/homework_db
   ```

2. **Set strong secrets**:
   ```bash
   openssl rand -hex 32  # Generate SECRET_KEY
   ```

3. **Configure reverse proxy** (nginx/Apache)

4. **Use process manager** (PM2, supervisor, systemd)

5. **Set up SSL/TLS certificates**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the logs for error details
3. Ensure DeepSeek API key is valid
4. Verify database connection

## 🔧 Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "Add new feature"

# Apply migration  
alembic upgrade head
```

### Code Formatting
```bash
# Install formatting tools
pip install black isort

# Format code
black .
isort .
```