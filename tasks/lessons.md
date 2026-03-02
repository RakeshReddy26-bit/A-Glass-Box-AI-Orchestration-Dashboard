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
