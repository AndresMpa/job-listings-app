"""Postgres persistence for scored job listings.

Kept intentionally small: one table, one upsert function, one read function.
The rest of the pipeline (fetchers, filters, scoring) doesn't know the DB
exists — cli.py is the only caller of save_jobs().
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.dialects.postgresql import ARRAY, insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .config import DatabaseConfig
from .models import JobListing


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class JobRecord(Base):
    __tablename__ = "job_listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(512))
    company: Mapped[str] = mapped_column(String(256), default="")
    url: Mapped[str] = mapped_column(String(1024), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    salary: Mapped[str | None] = mapped_column(String(128), nullable=True)
    location: Mapped[str] = mapped_column(String(256), default="")
    posted_date: Mapped[str] = mapped_column(String(64), default="")

    fit_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    income_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    outreach_draft: Mapped[str | None] = mapped_column(Text, nullable=True)

    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


def get_engine(db_cfg: DatabaseConfig):
    if not db_cfg.url:
        raise ValueError("database.url is not configured")
    return create_engine(db_cfg.url, pool_pre_ping=True)


def init_db(db_cfg: DatabaseConfig) -> None:
    """Create the job_listings table if it doesn't exist yet."""
    Base.metadata.create_all(get_engine(db_cfg))


def save_jobs(jobs: list[JobListing], db_cfg: DatabaseConfig) -> int:
    """Upsert jobs by URL. Returns the number of rows written."""
    if not jobs:
        return 0
    engine = get_engine(db_cfg)
    Base.metadata.create_all(engine)

    session_factory = sessionmaker(bind=engine)
    with session_factory() as session:  # type: Session
        for job in jobs:
            values = dict(
                source=job.source,
                title=job.title,
                company=job.company,
                url=job.url,
                description=job.description,
                tags=list(job.tags),
                salary=job.salary,
                location=job.location,
                posted_date=job.posted_date,
                fit_score=job.fit_score,
                income_score=job.income_score,
                score=job.score,
                reasoning=job.reasoning,
                outreach_draft=job.outreach_draft,
                updated_at=datetime.now(timezone.utc),
            )
            stmt = insert(JobRecord).values(**values, url=job.url)
            stmt = stmt.on_conflict_do_update(index_elements=[JobRecord.url], set_=values)
            session.execute(stmt)
        session.commit()
    return len(jobs)


def fetch_jobs(
    db_cfg: DatabaseConfig,
    min_score: int | None = None,
    limit: int = 200,
    offset: int = 0,
) -> list[JobRecord]:
    engine = get_engine(db_cfg)
    session_factory = sessionmaker(bind=engine)
    with session_factory() as session:  # type: Session
        stmt = select(JobRecord).order_by(JobRecord.score.desc().nulls_last(), JobRecord.first_seen_at.desc())
        if min_score is not None:
            stmt = stmt.where(JobRecord.score >= min_score)
        stmt = stmt.limit(limit).offset(offset)
        return list(session.execute(stmt).scalars().all())
