# Spark Readiness Screen — deploy guide

Same GitHub-to-Render flow you ran for spark-eval and spark-metrics, but simpler:
this one has **no database and no password**, so there is nothing to provision and
no environment variables you must set. One web service, about $7/month.

---

## What this is

A public, no-login screening tool. A founder answers seven short sections and sees
a five-stage read of their technical and commercial readiness, a radar profile, and
a note pointing to the full in-program assessment.

Nothing is saved. Answers stay in the browser and never reach Spark. There is no
database on purpose.

Runs two ways with no code change:
- On your laptop: `python app.py`, then open http://127.0.0.1:5000
- On Render: `gunicorn app:app` (set automatically by the files below)

---

## Step 1 — Put the code on GitHub

1. Create a new repository named `spark-screen` (public or private, your call).
2. Upload every file in this folder, then **Commit changes**.

## Step 2 — Create the web service on Render

1. render.com → **New +** → **Web Service** → build from your `spark-screen` repo.
2. Settings:
   - Name: `spark-screen`
   - Runtime: Python 3
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
   - Instance type: the cheapest paid tier (so it never sleeps)
3. There are **no environment variables you must add.** Render will use the
   `render.yaml` in the repo, which sets the Python version and generates a
   SECRET_KEY for you. If you build the service by hand instead of from the
   blueprint, you can add `PYTHON_VERSION = 3.12.8` to be safe, but it is optional.
4. **Create Web Service** and watch the log until it goes live.

## Step 3 — Open it

Click your URL (`https://spark-screen.onrender.com`). No password. That's it.

---

## Files

- `app.py` — Flask app: serves the page and scores answers
- `scoring.py` — the gated TRL/CRL engine (validated against the workbook)
- `templates/index.html` — the whole front end (form, ladders, radar)
- `static/spark-logo.png` — Spark logo
- `requirements.txt`, `Procfile`, `render.yaml` — deployment

## If you want to change wording later

All seven sections and their statements live in `QUESTIONS` near the top of
`app.py`. The five stage names live in `STAGES` in `scoring.py`. Edit the text,
commit, and Render redeploys on push.
