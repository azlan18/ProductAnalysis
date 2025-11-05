## Setup

### Backend (FastAPI)
1. Open a terminal in the project root
2. Navigate to server
   - `cd server`
3. Create and activate a virtual environment (Python 3.12)
   - macOS/Linux: `python3.12 -m venv venv && source venv/bin/activate`
   - Windows (PowerShell): `py -3.12 -m venv venv; .\\venv\\Scripts\\Activate.ps1`
4. Install dependencies
   - `pip install -r requirements.txt`
5. Create `.env` from `.env.example` and fill your keys
6. Run the server
   - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### Frontend (React + Vite)
1. Open a new terminal in the project root
2. Navigate to client
   - `cd client`
3. Install dependencies
   - `npm install`
4. Start the dev server
   - `npm run dev`

### Default URLs
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:5173` (or the port Vite shows)


