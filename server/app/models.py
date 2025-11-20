from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class DocType(str, Enum):
    docx = "docx"
    pptx = "pptx"


class ProjectStatus(str, Enum):
    draft = "draft"
    generating = "generating"
    ready = "ready"


class FeedbackChoice(str, Enum):
    like = "like"
    dislike = "dislike"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    full_name: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    title: str
    topic: str
    doc_type: DocType
    status: ProjectStatus = Field(default=ProjectStatus.draft)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentSection(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    title: str
    position: int
    content: str = Field(default="")
    feedback: Optional[FeedbackChoice] = None
    last_comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Revision(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    section_id: int = Field(foreign_key="documentsection.id")
    prompt: Optional[str] = None
    response: Optional[str] = None
    comment: Optional[str] = None
    feedback: Optional[FeedbackChoice] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

