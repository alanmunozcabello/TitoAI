from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from services.ask_tito import ask_tito_stream

router = APIRouter()

class Mensaje(BaseModel):
    mensaje: str = Field(min_length=1, max_length=100)

@router.post("/ia/chat/{mensaje}")
def route_chat_ia(mensaje: str):
    """
    Ruta para enviar mensaje a la IA y recibir respuesta en streaming
    """
    return StreamingResponse(ask_tito_stream(mensaje), media_type="text/plain")
