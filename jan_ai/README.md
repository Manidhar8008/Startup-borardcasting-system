# Jan.ai - AI Media Manager

A production-ready MVP for managing, scheduling, and generating AI posts for social media.

## Tech Stack
- **Backend:** Python (FastAPI)
- **Database:** PostgreSQL (SQLAlchemy)
- **AI:** OpenAI API
- **Automation:** Playwright

## Setup Instructions

1. **Install Dependencies**
   ```bash
   cd jan_ai
   pip install -r requirements.txt
   playwright install
   ```

2. **Environment Variables**
   Create a `.env` file in the root `jan_ai` folder:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/dbname
   OPENAI_API_KEY=your_openai_api_key
   ```
   *(Note: if DATABASE_URL is not set, it defaults to a local SQLite db for testing)*

3. **Run the API Server**
   ```bash
   cd jan_ai
   uvicorn backend.main:app --reload
   ```

4. **Access the Application**
   - API Docs: `http://localhost:8000/docs`
   - Frontend: `http://localhost:8000/`
