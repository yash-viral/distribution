from models.agent_models import AgentManager

class AgentService:
    def __init__(self):
        self.agent_manager = AgentManager()
    
    def chat_with_agent(self, agent_name: str, message: str):
        return self.agent_manager.chat_with_agent(agent_name, message)
    
    def get_available_agents(self, licensed_agents: list):
        return self.agent_manager.get_available_agents(licensed_agents)