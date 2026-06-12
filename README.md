# ATS Platform AI

An AI-powered Applicant Tracking System (ATS) that automates resume parsing, candidate ranking, and job matching using Machine Learning.

## Features

* Resume Upload (PDF & DOCX)
* Resume Parsing
* Skill Extraction
* TF-IDF Vectorization
* ATS Score Generation
* Candidate Ranking Engine
* Job Description Management
* Dashboard Analytics
* FastAPI Backend
* React + TypeScript Frontend
* SQLite Database
* Swagger API Documentation

## Tech Stack

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS

### Backend

* FastAPI
* SQLAlchemy
* Alembic

### Machine Learning

* Scikit-Learn
* TF-IDF Vectorizer
* Cosine Similarity
* NLTK

### Database

* SQLite

## ML Pipeline

1. Resume Upload
2. PDF/DOCX Parsing
3. Text Preprocessing
4. Skill Extraction
5. TF-IDF Vectorization
6. Cosine Similarity Scoring
7. ATS Score Calculation
8. Candidate Ranking

## Local Setup

### Backend

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

alembic upgrade head

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

## API Documentation

Swagger Docs:

```text
http://localhost:8000/api/docs
```

## Project Structure

backend/

* api/
* models/
* schemas/
* services/
* ml/

frontend/

* pages/
* components/
* services/
* hooks/

## Future Improvements

* PostgreSQL Support
* JWT Authentication
* Email Notifications
* Resume Recommendation Engine
* Advanced ML Ranking Models

## Author

Prasad Bole

GitHub:
https://github.com/prasadbole-12
