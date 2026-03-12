# Atlas Lessons Learned
Auto-updated when mistakes happen.
Atlas reviews this at the start of every session.

## Lesson 001 — SkillVector connection
Pattern: Always verify SkillVector is alive FIRST before any pipeline step.
If connection fails, wait 30 seconds and retry once. Render free tier sleeps.
Fix: call verify_skillevector_connection() as step 1 always.

## Lesson 002 — .env loading
Pattern: Always call load_dotenv() at top of every integration file.
Without it, os.getenv() returns None and all API calls fail with 403.
Fix: first line of every file = from dotenv import load_dotenv / load_dotenv()

## Lesson 003 — Git push conflicts
Pattern: Always git pull --rebase before git push.
Without pull, push fails with non-fast-forward error.
Fix: always run pull before push in github_pusher.py

## Lesson 004 — Twitter API
Pattern: Twitter API requires payment for write access.
Do not attempt Twitter direct API. Use Zapier or Buffer instead.
Fix: route all Twitter posts through Zapier webhook.

## Lesson 005 — LinkedIn OAuth
Pattern: LinkedIn auth codes expire in 30 seconds.
Client credentials flow does not work for posting.
Fix: use Zapier for LinkedIn posting — no OAuth needed.

## Lesson 006 — API auto-recovery
Pattern: Railway can go down due to deploys, cold starts, or OOM crashes.
Atlas now auto-detects downtime and pushes an empty commit to trigger Railway redeploy.
If down 2+ hours (consecutive hourly pings), redeploy is triggered automatically.
After redeploy, Atlas waits 2 min and verifies. If still down, sends alert email.

## Lesson 007 — Always check production URL
Pattern: SKILLEVECTOR_URL in .env points to localhost for local dev.
Health checks must always hit https://api.skill-vector.com (the real production URL).
Fix: SKILLEVECTOR_PROD_URL constant always points to production domain.


## Lesson (auto 2026-03-09)
Pipeline confidence: 45%. Failed steps: research=unknown, content=unknown, save=unknown, code_improvement=failed. Action: investigate and fix before next run.


## Lesson (auto 2026-03-10)
Pipeline confidence: 50%. Failed steps: research=unknown, content=unknown, save=unknown. Action: investigate and fix before next run.


## Lesson (auto 2026-03-11)
Pipeline confidence: 50%. Failed steps: research=unknown, content=unknown, save=unknown. Action: investigate and fix before next run.


## Lesson (auto 2026-03-12)
Pipeline confidence: 50%. Failed steps: research=unknown, content=unknown, save=unknown. Action: investigate and fix before next run.
