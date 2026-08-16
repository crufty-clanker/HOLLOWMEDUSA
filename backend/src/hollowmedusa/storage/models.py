from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, String

from .database import Base


class RunModel(Base):
    __tablename__ = "runs"

    id = Column(String, primary_key=True)
    status = Column(String, default="pending")
    state = Column(JSON, default=dict)
    step_results = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AgentModel(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    config = Column(JSON, default=dict)


class ModelModel(Base):
    __tablename__ = "models"

    id = Column(String, primary_key=True)
    config = Column(JSON, default=dict)


class ContextModel(Base):
    __tablename__ = "contexts"

    id = Column(String, primary_key=True)
    config = Column(JSON, default=dict)


class GraphModel(Base):
    __tablename__ = "graphs"

    id = Column(String, primary_key=True, default="default")
    topology = Column(JSON, default=dict)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True)
    api_key = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
