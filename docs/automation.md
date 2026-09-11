# Automation

Per the thesis plan's original scope, automation is handled with
Windows Task Scheduler (or Cron on macOS/Linux) — not a dedicated
scheduler service like Airflow, which is explicitly out of scope
(see `docs/requirements.md`, Scope).

## Flow

```
Trigger (Task Scheduler / Cron)
       │
       ▼
  pipeline.py
       │
       ▼
    Extract
       │
       ▼
   Transform
       │
       ▼
    Validate
       │
       ▼
      Load
```

`pipeline.py` itself is unaware of what triggered it — it runs the
same way whether started manually, by Task Scheduler, or by cron.
This keeps the automation layer thin: a scheduler simply needs to run
one script (`scripts/run_pipeline.bat` on Windows, or
`scripts/run_pipeline.sh` on macOS/Linux) on the desired schedule.

## Windows Task Scheduler setup

1. Open Task Scheduler → **Create Basic Task**
2. Name it (e.g. "Educational Data Pipeline"), choose a trigger
   (Daily, Weekly, etc.)
3. Action: **Start a program**
   - Program/script: full path to `scripts/run_pipeline.bat`
4. Finish — the task will run `pipeline.py` on schedule, logging to
   `logs/pipeline.log` exactly as a manual run does

## Cron setup (macOS/Linux)

```bash
crontab -e
# Add, e.g. daily at 2am:
0 2 * * * /path/to/educational-data-pipeline/scripts/run_pipeline.sh
```

## Verifying an automated run

Because logging is identical whether triggered manually or by a
scheduler (see Phase 2 Day 5), a scheduled run is verifiable the same
way: check `logs/pipeline.log` for a new
`Pipeline started` ... `Pipeline completed in Xs` block with the
expected timestamp.
