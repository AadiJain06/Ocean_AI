from fastapi import APIRouter, Depends

from ..auth import get_current_user
from ..models import User
from ..schemas import TemplateRequest, TemplateResponse
from ..services.llm import llm_service


router = APIRouter(prefix="/templates", tags=["templates"])


@router.post("/outline", response_model=TemplateResponse)
def suggest_outline(payload: TemplateRequest, current_user: User = Depends(get_current_user)) -> TemplateResponse:
    titles = llm_service.generate_outline(payload.topic, payload.doc_type, payload.item_count)
    return TemplateResponse(titles=titles)

