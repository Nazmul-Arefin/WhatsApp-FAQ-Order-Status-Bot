# Backend (FastAPI)
## Run locally
```bash
# 1) Create and fill .env
cp .env.example .env
# 2) Create venv and install
python -m venv .venv
source .venv/bin/activate # Windows PowerShell: .venv\\Scripts\
\Activate.ps1
pip install -r requirements.txt
# 3) Start API
uvicorn app:app --host 0.0.0.0 --port 8000 --reload