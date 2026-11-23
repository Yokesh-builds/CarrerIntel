
import os

from dotenv import load_dotenv

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
    or_,
    func
)

from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///careerintel.db"
)


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)


Session = sessionmaker(
    bind=engine,
    expire_on_commit=False
)


Base = declarative_base()


class Job(Base):

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)

    source = Column(String(30), nullable=False)
    external_id = Column(String(150), nullable=False)

    title = Column(String(300), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(300))

    department = Column(String(200))
    employment_type = Column(String(150))
    posted_at = Column(String(100))

    job_url = Column(String(1000))
    description = Column(Text)

    __table_args__ = (
        UniqueConstraint(
            "source",
            "external_id",
            name="uq_source_external_id"
        ),
        Index("idx_job_title", "title"),
        Index("idx_job_company", "company"),
        Index("idx_job_location", "location"),
        Index("idx_job_source", "source")
    )


def initialize_database():

    Base.metadata.create_all(engine)


def save_jobs(jobs):

    session = Session()

    inserted = 0
    updated = 0

    try:

        for item in jobs:

            existing = session.query(Job).filter_by(
                source=item["source"],
                external_id=item["external_id"]
            ).first()

            if existing:

                for key, value in item.items():
                    setattr(existing, key, value)

                updated += 1

            else:

                session.add(Job(**item))
                inserted += 1

        session.commit()

        return inserted, updated

    except Exception:

        session.rollback()
        raise

    finally:

        session.close()


def search_jobs(
    keyword="",
    source="",
    company="",
    location="",
    page=1,
    per_page=20
):

    session = Session()

    try:

        query = session.query(Job)

        searchable_fields = [
            Job.title,
            Job.company,
            Job.location,
            Job.department,
            Job.description
        ]

        keywords = [
            word.strip()
            for word in keyword.split(",")
            if word.strip()
        ]

        # AND logic between keywords
        for word in keywords:

            pattern = f"%{word}%"

            query = query.filter(
                or_(
                    *[
                        field.ilike(pattern)
                        for field in searchable_fields
                    ]
                )
            )

        if source:

            query = query.filter(
                Job.source == source
            )

        if company:

            query = query.filter(
                Job.company.ilike(f"%{company}%")
            )

        if location:

            query = query.filter(
                Job.location.ilike(f"%{location}%")
            )

        total = query.count()

        jobs = query.order_by(
            Job.posted_at.desc(),
            Job.id.desc()
        ).offset(
            (max(1, page) - 1) * per_page
        ).limit(per_page).all()

        return jobs, total

    finally:

        session.close()


def get_job_by_id(job_id):

    session = Session()

    try:

        return session.query(Job).filter(
            Job.id == job_id
        ).first()

    finally:

        session.close()


def get_dashboard_statistics():

    session = Session()

    try:

        total_jobs = session.query(
            func.count(Job.id)
        ).scalar() or 0

        total_companies = session.query(
            func.count(func.distinct(Job.company))
        ).scalar() or 0

        total_sources = session.query(
            func.count(func.distinct(Job.source))
        ).scalar() or 0

        return {
            "total_jobs": total_jobs,
            "total_companies": total_companies,
            "total_sources": total_sources
        }

    finally:

        session.close()


def get_filter_options():

    session = Session()

    try:

        companies = [
            item[0]
            for item in session.query(
                Job.company
            ).filter(
                Job.company.isnot(None)
            ).distinct().order_by(Job.company).all()
        ]

        locations = [
            item[0]
            for item in session.query(
                Job.location
            ).filter(
                Job.location.isnot(None)
            ).distinct().order_by(Job.location).all()
        ]

        return companies, locations

    finally:

        session.close()
