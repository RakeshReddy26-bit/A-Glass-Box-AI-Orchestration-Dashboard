**Show IH: SkillVector - AI that identifies skill gaps blocking ML engineers from senior roles**

After seeing great ML engineers stuck at mid-level despite strong technical chops, I realized the issue wasn't coding ability - it was unknown skill gaps around business communication, system design, and stakeholder management.

Built SkillVector to solve this. It's essentially pattern matching at scale:
- Scraped thousands of senior ML job postings 
- Used Claude Sonnet to extract and categorize skill requirements
- Built a Neo4j knowledge graph linking skills to career outcomes
- Pinecone for semantic matching of user profiles against requirements
- FastAPI backend with a simple React frontend

Nothing groundbreaking technically, but addresses a real pain point. Early beta users are getting much more targeted career development instead of generic "learn leadership" advice.

Still rough around the edges, but the core insight seems valuable - most people don't know what they don't know about advancing.

https://skill-vector.com