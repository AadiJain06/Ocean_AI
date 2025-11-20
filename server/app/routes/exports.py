from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from ..auth import get_current_user
from ..database import get_session
from ..models import DocType, DocumentSection, Project, User
from ..routes.projects import _project_sections
from ..utils.docx_export import build_docx
from ..utils.pptx_export import build_pptx


router = APIRouter(prefix="/export", tags=["export"])


@router.get("/{project_id}")
def export_project(
    project_id: int,
    format: DocType,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Response:
    project = session.get(Project, project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    sections = _project_sections(session, project.id)
    if not sections:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No content to export")

    if format == DocType.docx:
        buffer = build_docx(project, sections)
        filename = f"{project.title}.docx"
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        buffer = build_pptx(project, sections)
        filename = f"{project.title}.pptx"
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

