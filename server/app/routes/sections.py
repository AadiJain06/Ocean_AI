from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..auth import get_current_user
from ..database import get_session
from ..models import DocumentSection, Project, Revision, User
from ..schemas import CommentRequest, FeedbackRequest, RefineRequest, SectionRead
from ..services.llm import llm_service


router = APIRouter(prefix="/sections", tags=["sections"])


def _load_section(session: Session, section_id: int, user: User) -> tuple[DocumentSection, Project]:
    section = session.get(DocumentSection, section_id)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    project = session.get(Project, section.project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    return section, project


@router.post("/{section_id}/refine", response_model=SectionRead)
def refine_section(
    section_id: int,
    payload: RefineRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> SectionRead:
    section, project = _load_section(session, section_id, current_user)
    updated_text = llm_service.refine_section(project.topic, section.title, section.content, payload.prompt)
    section.content = updated_text
    section.updated_at = datetime.utcnow()
    session.add(section)
    session.add(
        Revision(
            section_id=section.id,
            prompt=payload.prompt,
            response=updated_text,
        )
    )
    session.commit()
    session.refresh(section)
    return SectionRead.model_validate(section)


@router.post("/{section_id}/feedback", response_model=SectionRead)
def set_feedback(
    section_id: int,
    payload: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> SectionRead:
    section, _ = _load_section(session, section_id, current_user)
    section.feedback = payload.value
    section.updated_at = datetime.utcnow()
    session.add(section)
    session.add(Revision(section_id=section.id, feedback=payload.value))
    session.commit()
    session.refresh(section)
    return SectionRead.model_validate(section)


@router.post("/{section_id}/comment", response_model=SectionRead)
def add_comment(
    section_id: int,
    payload: CommentRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> SectionRead:
    section, _ = _load_section(session, section_id, current_user)
    section.last_comment = payload.comment
    section.updated_at = datetime.utcnow()
    session.add(section)
    session.add(Revision(section_id=section.id, comment=payload.comment))
    session.commit()
    session.refresh(section)
    return SectionRead.model_validate(section)

