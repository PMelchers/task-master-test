# Scheduled Trader Backend

This is the backend service for the Scheduled Trader application, built with FastAPI.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
.\venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```
DATABASE_URL=sqlite:///./scheduled_trader.db
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Run the development server:
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8080
API documentation will be available at http://localhost:8080/docs

## Project Structure

```
backend/
├── alembic/              # Database migrations
├── app/
│   ├── api/             # API routes
│   ├── core/            # Core functionality
│   ├── db/              # Database models and session
│   ├── schemas/         # Pydantic models
│   └── services/        # Business logic
├── tests/               # Test files
├── .env                 # Environment variables
├── main.py             # Application entry point
└── requirements.txt    # Project dependencies
``` 