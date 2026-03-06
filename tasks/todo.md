# Atlas Daily Task Plan v2.0
Last updated: auto-updated by Atlas

## Daily Pipeline (8 AM)
- [x] Step 1: Health check SkillVector API
- [x] Step 2: Research ML/AI career trends via Claude
- [x] Step 3: Generate content for 4 platforms (LinkedIn, Reddit, Twitter, Indie Hackers)
- [x] Step 3b: Monday image prompt (Mondays only)
- [x] Step 4: Save posts to posts/ with dated filenames
- [x] Step 5: Send email digest (3x retry)
- [x] Step 6: Code improvement (Mon/Wed/Fri only)
- [x] Step 7: Weekly analytics (Sunday only)
- [x] Step 8: Competitor monitoring

## Confidence Tracking
- Pipeline reads tasks/lessons.md before each run
- Failed steps auto-record lessons for next run
- Confidence score logged at end of each run

## Scheduling
- Crontab: daily at 8 AM + hourly health pings
- Manual: python scheduler.py --run-now
