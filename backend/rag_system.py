import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEndpoint
from langchain.schema import HumanMessage, SystemMessage

# MOCK KNOWLEDGE BASE
IMEC_CONTEXT = """
The India-Middle East-Europe Economic Corridor (IMEC) is a planned economic corridor that aims to bolster economic development by fostering connectivity and economic integration between Asia, the Arabian Gulf, and Europe.
The corridor consists of two separate corridors: the east corridor connecting India to the Arabian Gulf and the northern corridor connecting the Arabian Gulf to Europe.
It will include a railway that, upon completion, will provide a reliable and cost-effective cross-border ship-to-rail transit network to supplement existing maritime and road transport routes.
IMEC is seen as a counter to China's Belt and Road Initiative (BRI).
Key benefits include:
1. Reduced transit time by up to 40% compared to the Suez Canal.
2. Lower CO2 emissions.
3. Enhanced geopolitical stability/integration.
Potential risks include: 
1. Geopolitical instability in the Middle East (e.g. Israel-Jordan border).
2. Heatwaves affecting rail infrastructure in Saudi Arabia.
"""

class RAGChatbot:
    def __init__(self):
        # 1. Try Groq (Fastest)
        self.groq_key = os.environ.get("GROQ_API_KEY")
        
        # 2. Try HuggingFace (Free Open Source API)
        self.hf_token = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        
        self.llm = None
        
        if self.groq_key:
            print("Chatbot: Using Groq (Llama 3)")
            self.llm = ChatGroq(temperature=0, groq_api_key=self.groq_key, model_name="llama3-8b-8192")
            
        elif self.hf_token:
            print("Chatbot: Using HuggingFace API (Mistral-7B)")
            # repo_id="mistralai/Mistral-7B-Instruct-v0.3" is a good free option
            self.llm = HuggingFaceEndpoint(
                repo_id="mistralai/Mistral-7B-Instruct-v0.3", 
                huggingfacehub_api_token=self.hf_token,
                temperature=0.1
            )
        else:
            print("WARNING: No API Key found (Groq or HF). Chatbot running in RULE-BASED MODE.")

    def query(self, user_input, simulation_context=None):
        """
        user_input: The user's question.
        simulation_context: Current state of the digital twin
        """
        
        # 1. REAL AI MODE (If API Key exists)
        if self.llm:
            try:
                system_prompt = f"Context: {IMEC_CONTEXT}\nState: {simulation_context}\nAnswer concisely."
                messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_input)]
                return self.llm.invoke(messages).content
            except:
                pass # Fallback to rule-based if API fails

        # 2. SMART LOCAL MODE (No Credit Card / No API Key required)
        # This acts as a "fallback AI" for the demo
        user_input = user_input.lower()
        
        if "risk" in user_input or "conflict" in user_input:
            return "Analysis: Regional instability significantly impacts the Northern Corridor. Current conflict levels would add approximately 48-72 hours of border processing delays."
            
        elif "cost" in user_input or "price" in user_input:
            return "Economic Analysis: The IMEC rail network reduces shipping costs by ~30% compared to the Suez route by bypassing canal fees and reducing fuel consumption."
            
        elif "time" in user_input or "fast" in user_input or "how long" in user_input:
            return "Transit Calculation: The IMEC hybrid route (Ship-to-Rail) is projected to be 40% faster than the Suez Canal maritime route, saving roughly 8-10 days."
            
        elif "suez" in user_input:
            return "Comparative Data: The Suez Canal handles 12% of global trade but is a single point of failure. IMEC provides a critical redundancy layer for European energy security."
            
        elif "status" in user_input or "current" in user_input:
            if "blocked" in str(simulation_context).lower():
                return "CRITICAL ALERT: Suez Canal is currently BLOCKED. Recommended Action: Reroute all cargo via IMEC Rail Link immediately."
            else:
                return "System Status: All corridors operational. Optimal route depends on current fuel prices and piracy risk levels."

        return "I am the IMEC Strategic Advisor. I can analyze Risks, Costs, Transit Times, and Strategic trends for you. What would you like to know?"

# Singleton Instance
chatbot = RAGChatbot()

def chat_with_twin(message: str, sim_data: str = ""):
    return chatbot.query(message, sim_data)
