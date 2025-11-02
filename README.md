# 🧰 Setup Instructions

Follow these commands to set up and run the project.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d
```

migrations


```bash
python -m db.user
python -m db.ntc_labels
python -m db.manager_nta

```
import DB's

```bash
python -m app.notify_manager
python -m app.notify_assignee

```
