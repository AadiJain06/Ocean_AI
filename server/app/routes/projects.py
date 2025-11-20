from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..auth import get_current_user
from ..database import get_session
from ..models import DocumentSection, Project, ProjectStatus, Revision, User
from ..schemas import (
    GenerateRequest,
    ProjectCreate,
    ProjectDetail,
    ProjectRead,
    SectionRead,
)
from ..services.llm import llm_service


router = APIRouter(prefix="/projects", tags=["projects"])


def _project_sections(session: Session, project_id: int) -> List[DocumentSection]:
    return session.exec(
        select(DocumentSection).where(DocumentSection.project_id == project_id).order_by(DocumentSection.position)
    ).all()


def _to_detail(project: Project, sections: List[DocumentSection]) -> ProjectDetail:
    return ProjectDetail(
        id=project.id,
        title=project.title,
        topic=project.topic,
        doc_type=project.doc_type,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        sections=[SectionRead.model_validate(section) for section in sections],
    )


@router.get("/", response_model=list[ProjectRead])
def list_projects(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Project]:
    return session.exec(select(Project).where(Project.owner_id == current_user.id).order_by(Project.created_at)).all()


@router.post("/", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ProjectDetail:
    project = Project(
        owner_id=current_user.id,
        title=payload.title,
        topic=payload.topic,
        doc_type=payload.doc_type,
        status=ProjectStatus.draft,
    )
    session.add(project)
    session.commit()
    session.refresh(project)

    for section in payload.sections:
        session.add(
            DocumentSection(
                project_id=project.id,
                title=section.title,
                position=section.position,
            )
        )
    session.commit()

    sections = _project_sections(session, project.id)
    return _to_detail(project, sections)


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ProjectDetail:
    project = session.get(Project, project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    sections = _project_sections(session, project.id)
    return _to_detail(project, sections)


@router.post("/{project_id}/generate", response_model=ProjectDetail)
def generate_content(
    project_id: int,
    payload: GenerateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ProjectDetail:
    project = session.get(Project, project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    sections = _project_sections(session, project.id)
    if not sections:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project has no sections")

    project.status = ProjectStatus.generating
    session.add(project)
    session.commit()

    for section in sections:
        if not section.content or payload.regenerate:
            section.content = llm_service.generate_section(project.topic, section.title)
            section.updated_at = datetime.utcnow()
            session.add(section)
            session.add(
                Revision(
                    section_id=section.id,
                    prompt="initial generation" if not payload.regenerate else "regeneration",
                    response=section.content,
                )
            )

    project.status = ProjectStatus.ready
    project.updated_at = datetime.utcnow()
    session.add(project)
    session.commit()

    sections = _project_sections(session, project.id)
    return _to_detail(project, sections)

