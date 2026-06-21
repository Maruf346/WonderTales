# WonderTales Hub - Setup & Configuration Guide

## 📋 Overview

I've created all the necessary configuration files for your WonderTales project:

### Files Created:

1. **Root Level:**
   - `.env` - Master environment file with all services' configuration
   - `requirements.txt` - Combined Python dependencies for all services

2. **Backend Service:**
   - `backend/.env` - Django-specific environment variables
   - `backend/requirements.txt` - Django backend dependencies

3. **AI Service:**
   - `ai/.env` - FastAPI AI service environment variables
   - `ai/requirements.txt` - FastAPI AI service dependencies

4. **Frontend:**
   - `landingpage/.env` - Vite/React frontend environment variables

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+ (for frontend)
- PostgreSQL (for backend database)
- pip and npm/pnpm package managers

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env file with your database credentials and settings
nano .env  # or use your editor

# Run migrations
python manage.py migrate

# Create superuser (for admin)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Backend will be available at: `http://localhost:8000`

### 2. AI Service Setup

```bash
cd ai

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env file with your OpenAI and ElevenLabs API keys
nano .env

# Run development server
uvicorn main:app --reload --port 8050
```

AI Service will be available at: `http://localhost:8050`
API Docs: `http://localhost:8050/docs`

### 3. Frontend Setup

```bash
cd landingpage

# Install dependencies
npm install
# or
pnpm install

# Configure environment
# Edit .env file with your API URLs
nano .env

# Run development server
npm run dev
# or
pnpm dev
```

Frontend will be available at: `http://localhost:5173`

---

## 🔧 Environment Variables Guide

### Backend (.env)

**Security:**
- `SECRET_KEY` - Django secret key (generate a strong one for production)
- `DEBUG` - Set to `False` in production

**Database:**
- `DATABASE_URL` or individual `DB_*` variables - PostgreSQL connection details
- Use PostgreSQL for production (SQLite default in DEBUG mode)

**AWS S3 (Optional):**
- Required for production file storage
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- `AWS_STORAGE_BUCKET_NAME`

**Email:**
- Configure SMTP settings if you want to send emails
- Tested with Gmail (requires app-specific password)

**Authentication:**
- Social OAuth setup in Django admin (Google, Apple)
- JWT tokens configured automatically

### AI Service (.env)

**Required APIs:**
- `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys
- `ELEVENLABS_API_KEY` - Get from https://elevenlabs.io

**Voice IDs:**
- Pre-configured with ElevenLabs voice IDs for different age tiers
- Customize the voice IDs in `.env` to match your ElevenLabs account

**App Settings:**
- `APP_PORT` - Change to `8050` (or your preferred port)
- `AUDIO_STORAGE_DIR` - Where to store generated audio files
- `ALLOWED_ORIGINS` - CORS origins for frontend communication

### Frontend (.env)

- `VITE_API_URL` - Backend API URL (http://localhost:8000/api)
- `VITE_AI_API_URL` - AI Service API URL (http://localhost:8050/api)

---

## 📦 Dependency Summary

### Backend (Django)
- **Django 6.0.2** - Web framework
- **PostgreSQL** - Database
- **JWT Authentication** - Token-based auth
- **Django REST Framework** - API development
- **Unfold Admin** - Beautiful admin interface
- **S3/Boto3** - File storage
- **Sentry** - Error tracking

**Total:** 25+ dependencies

### AI Service (FastAPI)
- **FastAPI 0.136.1** - Web framework
- **OpenAI SDK** - LLM integration
- **ElevenLabs** - Text-to-speech
- **Pydantic** - Data validation
- **Async/Await** - Concurrent processing

**Total:** 15+ dependencies

### Frontend (Vite + React)
- **React 19.2.6** - UI library
- **React Router** - Navigation
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **Vite** - Build tool

---

## 🐳 Docker Setup

To run everything in Docker:

```bash
# Development
./docker-helper.sh up

# Production
docker-compose -f docker-compose.prod.yml up -d
```

Make sure `.env` files are properly configured before running Docker.

---

## 🔑 Important Configuration Notes

### 1. Secret Keys
- Never commit `.env` files to version control (use `.env.example` instead)
- Always generate unique secret keys for production
- Use strong, random values for sensitive keys

### 2. Database
- For local development: Use default settings or SQLite
- For production: Must use PostgreSQL with strong password
- Run migrations: `python manage.py migrate`

### 3. API Keys
- OpenAI: Get from https://platform.openai.com/api-keys
- ElevenLabs: Get from https://elevenlabs.io
- AWS (optional): Configure if using S3 storage

### 4. CORS Origins
- Add your frontend URL to `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
- Update when deploying to production

### 5. Email (Optional)
- Gmail users need to generate an app-specific password
- Configure in backend `.env` if needed

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Backend migrations run without errors
- [ ] Backend admin accessible at `http://localhost:8000/admin`
- [ ] AI Service docs accessible at `http://localhost:8050/docs`
- [ ] Frontend loads at `http://localhost:5173`
- [ ] Frontend can communicate with both APIs
- [ ] All required environment variables are set

---

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
psql -U postgres -d wondertales_db

# Reset database (development only)
python manage.py migrate
```

### API Key Errors
- Verify OpenAI API key is valid
- Check ElevenLabs API key permissions
- Ensure API keys are in `.env` files (not `.env.example`)

### CORS Errors
- Check frontend URL is in `CORS_ALLOWED_ORIGINS`
- Verify `ALLOWED_HOSTS` includes backend domain
- Restart servers after modifying CORS settings

### Port Already in Use
```bash
# Change ports in `.env` or start scripts:
# Backend: APP_PORT in .env
# AI: APP_PORT in ai/.env
# Frontend: Vite uses 5173 by default
```

---

## 📖 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [ElevenLabs Documentation](https://elevenlabs.io/docs)

---

## 📝 Next Steps

1. ✅ Create `.env` files → **DONE**
2. ✅ Create `requirements.txt` files → **DONE**
3. → Install dependencies for each service
4. → Configure database credentials
5. → Add API keys (OpenAI, ElevenLabs)
6. → Run migrations
7. → Start development servers
8. → Test API connectivity

Happy coding! 🚀
