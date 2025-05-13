from langchain.agents import initialize_agent, Tool
from langchain.llms import HuggingFaceHub
from tools import symptom_checker

llm = HuggingFaceHub(repo_id="microsoft/phi-2", model_kwargs={"temperature": 0.7, "max_length": 100})

tools = [Tool(name="Symptom Checker", func=symptom_checker, description="Check illness based on symptoms.")]
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

def ask_bot(message):
    return agent.run(message)
