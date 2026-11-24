# MalipoHub

Business payments + payroll + stock + workforce platform built for Kenyan SMEs.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app app init-db
flask --app app seed
flask --app app run