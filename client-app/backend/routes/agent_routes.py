from fastapi import APIRouter
from pydantic import BaseModel
from services.agent_service import AgentService

router = APIRouter(tags=["agents"])
agent_service = AgentService()

class ChatMessage(BaseModel):
    agent: str
    message: str

@router.post("/chat")
async def chat_with_agent(chat: ChatMessage):
    response = agent_service.chat_with_agent(chat.agent, chat.message)
    return {"agent": chat.agent, "response": response}

@router.get("/available-agents")
async def get_available_agents():
    try:
        from services.license_service import LicenseService
        license_service = LicenseService()
        current_license = license_service.get_current_license()
        if not current_license:
            return {"agents": []}
        
        agents = agent_service.get_available_agents(current_license["agents"])
        return {"agents": agents}
    except Exception as e:
        print(f"DEBUG: Error getting available agents: {e}")
        return {"agents": []}