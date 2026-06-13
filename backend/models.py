from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class Province(Base):
    __tablename__ = "provinces"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    gaokao_mode = Column(String(20), nullable=False, default="传统高考")  # 新高考 / 传统高考

    universities = relationship("University", back_populates="province")
    scores = relationship("AdmissionScore", back_populates="province")
    plans = relationship("VolunteerPlan", back_populates="province")


class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=False)
    level = Column(String(20), nullable=False, default="普通")  # 985 / 211 / 双一流 / 普通
    utype = Column("type", String(20), nullable=False, default="综合")  # 综合/理工/师范/医药/农林/财经/政法/...
    website = Column(String(200))
    logo_url = Column(String(500))

    province = relationship("Province", back_populates="universities")
    scores = relationship("AdmissionScore", back_populates="university")


class Major(Base):
    __tablename__ = "majors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)  # 哲学/经济学/法学/教育学/文学/历史学/理学/工学/农学/医学/管理学/艺术学
    code = Column(String(20), unique=True, nullable=False)

    scores = relationship("AdmissionScore", back_populates="major")


class AdmissionScore(Base):
    __tablename__ = "admission_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=False)
    year = Column(Integer, nullable=False)
    batch = Column(String(20), nullable=False, default="本科批")  # 本科批 / 本科一批 / 本科二批 / 专科批
    subject_group = Column(String(20), nullable=False, default="不限")  # 物理/历史/不限
    min_score = Column(Float)
    min_rank = Column(Integer)
    avg_score = Column(Float)
    avg_rank = Column(Integer)
    max_score = Column(Float)
    enrollment_count = Column(Integer, default=0)

    university = relationship("University", back_populates="scores")
    major = relationship("Major", back_populates="scores")
    province = relationship("Province", back_populates="scores")


class VolunteerPlan(Base):
    __tablename__ = "volunteer_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, default="我的志愿方案")
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=False)
    score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    subject_group = Column(String(20), nullable=False, default="物理")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    province = relationship("Province", back_populates="plans")
    items = relationship("VolunteerItem", back_populates="plan", order_by="VolunteerItem.priority",
                         cascade="all, delete-orphan")


class VolunteerItem(Base):
    __tablename__ = "volunteer_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("volunteer_plans.id"), nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)
    priority = Column(Integer, nullable=False)
    note = Column(Text, default="")

    plan = relationship("VolunteerPlan", back_populates="items")
    university = relationship("University")
    major = relationship("Major")
