from pydantic import BaseModel, Field

class ChatConsulta(BaseModel):
    """
    Modelo para consulta al chatbot
    """
    texto: str = Field(
        None,
        max_length=5000,
        description="Texto de la consulta del usuario"
    )
