
glyphfeed_bp = Blueprint('glyphfeed', __name__)

@glyphfeed_bp.route("/glyphfeed", methods=["GET"])
def glyphfeed():
    from fastapi.responses import JSONResponse
    return JSONResponse(content={"message": "Glyphfeed endpoint"})

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/glyphfeed")
def glyphfeed():
    return {"message": "Glyphfeed endpoint"}
