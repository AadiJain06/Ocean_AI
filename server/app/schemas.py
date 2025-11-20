from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from .models import DocType, FeedbackChoice, ProjectStatus


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class SectionConfig(BaseModel):
    title: str
    position: int


class ProjectCreate(BaseModel):
    title: str
    topic: str
    doc_type: DocType
    sections: List[SectionConfig]


class ProjectRead(BaseModel):
    id: int
    title: str
    topic: str
    doc_type: DocType
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SectionRead(BaseModel):
    id: int
    title: str
    position: int
    content: str
    feedback: Optional[FeedbackChoice]
    last_comment: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectDetail(ProjectRead):
    sections: List[SectionRead]


class GenerateRequest(BaseModel):
    regenerate: bool = False


class RefineRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000, description="Refinement instruction for the section")


class FeedbackRequest(BaseModel):
    value: FeedbackChoice


class CommentRequest(BaseModel):
    comment: str = Field(..., min_length=2)


class TemplateRequest(BaseModel):
    topic: str
    doc_type: DocType
    item_count: int = Field(default=5, ge=3, le=15)


class TemplateResponse(BaseModel):
    titles: List[str]

