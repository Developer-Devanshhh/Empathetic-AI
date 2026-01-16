import json
import os
import asyncio
import google.generativeai as genai
from typing import List, Dict

from app.utils.safety import check_safety
from app.utils.chroma_client import query_similar, get_recent_entries

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "models/gemini-2.5-flash-preview-05-20"

class Orchestrator:
    def __init__(self):
        self.personas = self._load_personas()
        self.model = genai.GenerativeModel(MODEL_NAME)

    def _load_personas(self) -> Dict[str, dict]:
        path = os.path.join(os.path.dirname(__file__), "..", "agent_configs", "default_personas.json")
        try:
            with open(path, "r") as f:
                data = json.load(f)
                return {p["id"]: p for p in data}
        except Exception as e:
            print(f"[ERROR] Failed to load personas: {e}")
            return {}

    def get_personas(self) -> List[dict]:
        return list(self.personas.values())

    async def _generate_agent_response(self, agent_id: str, user_text: str, context: str) -> dict:
        """Call Gemini for a single agent."""
        persona = self.personas.get(agent_id)
        if not persona:
            return {"agent_id": agent_id, "response": "Error: Agent not found."}

        prompt = f"""
        ROLE: {persona['role']}
        TASK: {persona['system_prompt']}
        
        CONTEXT (Use only if relevant to your role):
        {context}
        
        USER INPUT:
        {user_text}
        
        Respond naturally in character. Keep it concise (under 3 sentences).
        """
        
        try:
            # We use the async generation method if available, else standard in a thread
            # genai library 'generate_content_async' is available in newer versions
            response = await self.model.generate_content_async(prompt)
            text = response.text if response.text else "..."
            return {"agent_id": agent_id, "name": persona["name"], "response": text.strip(), "color": persona.get("color", "gray")}
        except Exception as e:
            print(f"[{agent_id}] Generation failed: {e}")
            return {"agent_id": agent_id, "name": persona["name"], "response": "I'm having trouble thinking right now.", "color": "gray"}

    async def process_message(self, user_text: str, active_agent_ids: List[str], user_id: str, collection) -> dict:
        """
        Orchestrates the multi-agent response.
        1. SAFETY CHECK (Raw Input)
        2. Context Retrieval
        3. Parallel Agent Execution
        """
        # 1️⃣ SAFETY CHECK (CRITICAL: Must be first)
        safety_res = check_safety(user_text)
        if not safety_res["is_safe"]:
            return {
                "is_safe": False,
                "crisis_message": safety_res["response_message"],
                "responses": []
            }

        # 2️⃣ RETRIEVAL (Only if safe)
        rag_docs = query_similar(collection, user_text, n_results=3)
        recent_entries = get_recent_entries(collection, user_id, limit=3)
        
        # Format contexts types
        rag_context_str = "\n".join(rag_docs) if rag_docs else "No long-term memories found."
        recent_str = "\n".join([f"- {e['text']}" for e in recent_entries]) if recent_entries else "No recent session history."

        # 3️⃣ EXECUTOR LOOP
        tasks = []
        for agent_id in active_agent_ids:
            persona = self.personas.get(agent_id)
            if not persona:
                continue
                
            # Filter context based on access boundaries
            built_context = ""
            access = persona.get("memory_access", [])
            
            if "emotional_history" in access:
                built_context += f"\n[Relevant Past Memories]:\n{rag_context_str}\n"
            
            if "recent_session" in access:
                built_context += f"\n[Recent Conversation]:\n{recent_str}\n"
            
            tasks.append(self._generate_agent_response(agent_id, user_text, built_context))

        # Run in parallel
        agent_responses = await asyncio.gather(*tasks)

        return {
            "is_safe": True,
            "responses": agent_responses
        }

# Global Instance
orchestrator = Orchestrator()
