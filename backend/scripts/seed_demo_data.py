"""Seed demo data for portfolio screenshots.

Usage: docker exec autoposter-api python scripts/seed_demo_data.py
"""
import os
import sys
import uuid
import random
from datetime import datetime, timedelta

sys.path.insert(0, "/app")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL_SYNC = os.environ.get(
    "DATABASE_URL_SYNC", "postgresql+psycopg2://appuser:changeme@postgres:5432/autoposter"
)

engine = create_engine(DATABASE_URL_SYNC)
Session = sessionmaker(bind=engine)

from app.models.post import Post, PostStatus, PostType
from app.models.page import Page
from app.models.publish_log import PublishLog, PublishResult
from app.models.engagement import Engagement

# --- Content templates ---
POSTS_CONTENT = [
    ("New feature launch: Smart scheduling with timezone support. Set it once, publish everywhere.", "text"),
    ("Did you know? Posts published between 6-8 PM get 2x more engagement. Our heatmap proves it.", "text"),
    ("What's your favorite tool for content planning? Drop your answer below.", "text"),
    ("Version 2.1 is here! Queue management, bulk import, and analytics dashboard.", "text"),
    ("Behind the scenes: How we built a retry system that handles 99.5% of API failures automatically.", "text"),
    ("Monday motivation: Consistency beats perfection. Schedule your week in 10 minutes.", "text"),
    ("Pro tip: Use bulk import to schedule 100+ posts from a single CSV file.", "text"),
    ("Our engagement tracking shows evening posts outperform morning ones by 40%.", "text"),
    ("New integration: Telegram channels now supported with full retry logic and error handling.", "text"),
    ("Content calendar tip: Plan your week on Sunday, let automation handle the rest.", "text"),
    ("Just shipped: Real-time WebSocket updates. Watch your posts publish live.", "text"),
    ("Security update: All tokens now encrypted at rest with Fernet key rotation.", "text"),
    ("Ask me anything about social media automation. What would you automate first?", "text"),
    ("The 80/20 rule of content: 80% value, 20% promotion. Our queue makes it easy to balance.", "text"),
    ("We analyzed 10,000 posts. Best times: Tue 6PM, Thu 7PM, Sat 10AM.", "text"),
    ("Feature spotlight: Error spike protection auto-pauses channels after 3 consecutive failures.", "text"),
    ("Quick poll: Do you schedule posts daily, weekly, or monthly?", "text"),
    ("Tip: Set up recurring schedule slots for consistent posting without manual work.", "text"),
    ("How we handle rate limits: exponential backoff with 3 retry attempts. Zero lost posts.", "text"),
    ("Milestone: 1000 posts published automatically. Zero manual intervention needed.", "text"),
    ("Weekend content performs differently. Our heatmap helps you find the sweet spot.", "text"),
    ("Bulk import just got better: support for CSV and JSON with validation.", "text"),
    ("Content repurposing tip: Turn one blog post into 5 social media posts.", "text"),
    ("The analytics dashboard now shows top posts by engagement. Know what works.", "text"),
    ("Docker Compose makes deployment a single command. 7 containers, zero config.", "text"),
    ("Product update: Custom schedule picker with quick presets and timezone display.", "text"),
    ("Engagement tracking at 1h, 4h, and 24h after publish. Data-driven decisions.", "text"),
    ("Alert system: Get notified via Telegram when a post fails or your queue is empty.", "text"),
    ("Cross-platform publishing: Same content, multiple channels, one queue.", "text"),
    ("The drag-and-drop queue lets you reorder priorities in seconds.", "text"),
    ("Visual timeline view: See your entire content plan at a glance.", "text"),
    ("API-first design: Every feature accessible via REST API.", "text"),
    ("TypeScript strict mode + 96 tests = code you can trust in production.", "text"),
    ("Image posts with MinIO S3 storage. Upload, schedule, publish automatically.", "photo"),
    ("Link preview posts: Share articles with automatic metadata extraction.", "link"),
    ("New: Week calendar view inspired by Hootsuite. Click any slot to create a post.", "text"),
    ("Our retry logic saved 47 posts from permanent failure last month.", "text"),
    ("Content batching: Create 50 posts in one session, schedule across 2 weeks.", "text"),
    ("Multi-channel support: Telegram live, Twitter and Facebook ready to activate.", "text"),
    ("Privacy first: Tokens encrypted with Fernet, never exposed in API responses.", "text"),
    ("The publishing log shows every attempt, retry, and error. Full transparency.", "text"),
    ("Smart queue: Posts auto-advance to 'queued' status when scheduled time is set.", "text"),
    ("Platform-specific formatting: Character limits, image handling, link previews.", "text"),
    ("Real-time dashboard: WebSocket pushes updates as posts publish.", "text"),
    ("Deploy in 60 seconds: git clone, cp .env.example .env, docker-compose up.", "text"),
    ("FastAPI + async SQLAlchemy = 200+ concurrent requests with sub-50ms latency.", "text"),
    ("Celery Beat: Reliable task scheduling. Checks every 60 seconds, never misses.", "text"),
    ("PostgreSQL 16 with indexed queries. Schedule lookups under 1ms.", "text"),
    ("Redis as message broker + cache. Sub-millisecond task dispatch.", "text"),
    ("Our error classifier categorizes API errors: rate_limit, auth, content_policy, network.", "text"),
]


def seed():
    db = Session()
    try:
        # Check if already seeded
        existing = db.query(Post).count()
        if existing > 10:
            print(f"Already have {existing} posts. Skipping seed.")
            return

        # Get or create a page
        page = db.query(Page).first()
        if not page:
            print("No page found. Connect a channel first via Settings.")
            return

        page_id = str(page.id)
        now = datetime.utcnow()

        print(f"Seeding demo data for page: {page.name} ({page_id})")

        posts_created = []

        for i, (content, post_type) in enumerate(POSTS_CONTENT):
            status_roll = random.random()
            if status_roll < 0.65:
                status = PostStatus.published
                days_ago = random.randint(1, 30)
                hours = random.choice([9, 12, 15, 18, 20, 21])
                scheduled_at = now - timedelta(days=days_ago, hours=random.randint(0, 3))
                scheduled_at = scheduled_at.replace(hour=hours, minute=random.choice([0, 15, 30]))
                published_at = scheduled_at + timedelta(seconds=random.randint(5, 60))
            elif status_roll < 0.85:
                status = PostStatus.queued
                days_ahead = random.randint(0, 5)
                hours = random.choice([9, 12, 15, 18, 20])
                scheduled_at = now + timedelta(days=days_ahead)
                scheduled_at = scheduled_at.replace(hour=hours, minute=random.choice([0, 15, 30, 45]))
                published_at = None
            elif status_roll < 0.92:
                status = PostStatus.draft
                scheduled_at = None
                published_at = None
            else:
                status = PostStatus.failed
                days_ago = random.randint(1, 14)
                scheduled_at = now - timedelta(days=days_ago)
                scheduled_at = scheduled_at.replace(hour=random.choice([9, 18]), minute=0)
                published_at = None

            pt = PostType.text
            if post_type == "photo":
                pt = PostType.photo
            elif post_type == "link":
                pt = PostType.link

            post = Post(
                id=str(uuid.uuid4()),
                page_id=page_id,
                content_text=content,
                post_type=pt,
                status=status,
                order_index=i * 10 if status == PostStatus.queued else None,
                scheduled_at=scheduled_at,
                published_at=published_at,
                link_url="https://example.com/article" if pt == PostType.link else None,
                error_message="Rate limit exceeded (code 429). Retries exhausted." if status == PostStatus.failed else None,
            )
            db.add(post)
            posts_created.append(post)

        db.flush()

        # Create publish logs
        log_count = 0
        for post in posts_created:
            if post.status in (PostStatus.published, PostStatus.failed):
                # Main log entry
                log = PublishLog(
                    id=str(uuid.uuid4()),
                    post_id=post.id,
                    page_id=page_id,
                    result=PublishResult.success if post.status == PostStatus.published else PublishResult.permanent_error,
                    fb_post_id=str(random.randint(100000, 999999)) if post.status == PostStatus.published else None,
                    error_code=429 if post.status == PostStatus.failed else None,
                    error_message=post.error_message,
                    retry_count=0 if post.status == PostStatus.published else 3,
                    attempted_at=post.published_at or post.scheduled_at or now,
                )
                db.add(log)
                log_count += 1

                # Add retry logs for some published posts (shows retry working)
                if post.status == PostStatus.published and random.random() < 0.15:
                    retry_log = PublishLog(
                        id=str(uuid.uuid4()),
                        post_id=post.id,
                        page_id=page_id,
                        result=PublishResult.retriable_error,
                        error_code=429,
                        error_message="Too many requests. Retry after 30 seconds.",
                        retry_count=1,
                        attempted_at=post.published_at - timedelta(seconds=35),
                    )
                    db.add(retry_log)
                    log_count += 1

        # Create engagement data for published posts
        eng_count = 0
        for post in posts_created:
            if post.status == PostStatus.published:
                base_likes = random.randint(5, 200)
                fb_id = post.fb_post_id or str(random.randint(100000, 999999))
                engagement = Engagement(
                    id=str(uuid.uuid4()),
                    post_id=post.id,
                    fb_post_id=fb_id,
                    likes=base_likes,
                    comments=random.randint(0, base_likes // 4),
                    shares=random.randint(0, base_likes // 10),
                    fetched_at=post.published_at + timedelta(hours=24) if post.published_at else now,
                )
                db.add(engagement)
                eng_count += 1

        db.commit()

        published = sum(1 for p in posts_created if p.status == PostStatus.published)
        queued = sum(1 for p in posts_created if p.status == PostStatus.queued)
        draft = sum(1 for p in posts_created if p.status == PostStatus.draft)
        failed = sum(1 for p in posts_created if p.status == PostStatus.failed)

        print(f"Created {len(posts_created)} posts: {published} published, {queued} queued, {draft} draft, {failed} failed")
        print(f"Created {log_count} publish log entries")
        print(f"Created {eng_count} engagement records")
        print("Done!")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
