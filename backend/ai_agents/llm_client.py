import json
import logging
import os
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified LLM Client supporting Gemini, OpenAI, and deterministic heuristic fallback.
    Designed for SalesGenie AI Module 2: Lead Intelligence Engine.
    """
    def __init__(self):
        self.gemini_available = False
        self.openai_available = False
        self._init_providers()

    def _init_providers(self):
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                self.gemini_model = genai.GenerativeModel("gemini-1.5-pro")
                self.gemini_available = True
                logger.info("Gemini LLM Provider initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini: {e}")

        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=openai_key)
                self.openai_available = True
                logger.info("OpenAI LLM Provider initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI: {e}")

    def generate_json(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Invokes LLM with system and user prompts, expecting JSON response.
        Returns parsed dictionary, or None if LLM is unavailable or fails.
        """
        # Try Gemini first if available
        if self.gemini_available:
            try:
                full_prompt = f"{system_prompt}\n\nUSER DATA:\n{user_prompt}\n\nReturn ONLY a JSON object."
                response = self.gemini_model.generate_content(
                    full_prompt,
                    generation_config={"temperature": 0.2, "response_mime_type": "application/json"}
                )
                text = response.text
                return json.loads(text)
            except Exception as e:
                logger.warning(f"Gemini generation failed: {e}. Attempting fallback.")

        # Try OpenAI if Gemini unavailable
        if self.openai_available:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                text = response.choices[0].message.content
                return json.loads(text)
            except Exception as e:
                logger.warning(f"OpenAI generation failed: {e}. Attempting fallback.")

        return None


llm_client = LLMClient()
