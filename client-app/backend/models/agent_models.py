class AgentManager:
    def __init__(self):
        self.agents = {
            "agent1": "Hello I am agent 1",
            "agent2": "Hello I am agent 2", 
            "a1": "Hello I am a1",
            "a2": "Hello I am a2"
        }
    
    def chat_with_agent(self, agent_name: str, message: str) -> str:
        if agent_name not in self.agents:
            return f"Agent '{agent_name}' not found"
        
        base_response = self.agents[agent_name]
        return f"{base_response}. You said: '{message}'"
    
    def get_available_agents(self, licensed_agents: list) -> list:
        return [agent for agent in self.agents.keys() if agent in licensed_agents]