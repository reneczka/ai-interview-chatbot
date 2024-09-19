from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    job_location = Column(String, nullable=False)
    salary = Column(String, nullable=True)
    job_url = Column(String, nullable=False)
    type_of_work = Column(String, nullable=False)
    experience = Column(String, nullable=False)
    employment_type = Column(String, nullable=False)
    operating_mode = Column(String, nullable=False)
    job_description = Column(Text, nullable=True)
    technologies = relationship('Technology', back_populates='job')

class Technology(Base):
    __tablename__ = 'technologies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tech = Column(String, nullable=False)
    level = Column(String, nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    job = relationship('Job', back_populates='technologies')
