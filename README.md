# 🧰 Setup Instructions

Follow these commands to set up and run the project.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d

python -m db.user
python -m db.manager
python -m app.notify_manager
python -m app.notify_assignee
