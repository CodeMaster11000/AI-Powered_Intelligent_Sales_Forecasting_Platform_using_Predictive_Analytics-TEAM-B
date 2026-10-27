import json
import logging
import os
import re
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified Multi-LLM Client supporting:
    1. Google Gemini (gemini-1.5-pro / gemini-1.5-flash)
    2. OpenAI (gpt-4o / gpt-4o-mini)
    3. xAI Grok (grok-2-latest / grok-beta)
    4. Local LLMs via Ollama (llama3 / mistral / qwen2.5)
    5. Explicit provider selection without heuristic fallback output.
    """

    def __init__(self):
        self.gemini_available = False
        self.openai_available = False
        self.grok_available = False
        self.ollama_available = False
        self.last_provider_used: Optional[str] = None
        self._init_providers()

    def _init_providers(self):
        """Initializes API clients for all supported LLM providers."""
        # 1. Google Gemini
        gemini_key = os.environ.get("GEMINI_API_KEY")
        self.gemini_model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")
        if gemini_key:
            try:
                from google import genai

                self.gemini_client = genai.Client(
                    api_key=gemini_key,
                    http_options={"timeout": 2000},
                )
                self.gemini_available = True
                logger.info(f"Gemini LLM Provider initialized ({self.gemini_model_name}).")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini: {e}")

        # 2. OpenAI
        openai_key = os.environ.get("OPENAI_API_KEY")
        self.openai_model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        if openai_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=openai_key)
                self.openai_available = True
                logger.info(f"OpenAI LLM Provider initialized ({self.openai_model_name}).")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI: {e}")

        # 3. xAI Grok (OpenAI-compatible endpoint at https://api.x.ai/v1)
        xai_key = os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY")
        self.grok_model_name = os.environ.get("GROK_MODEL", "grok-2-latest")
        if xai_key:
            try:
                from openai import OpenAI
                self.grok_client = OpenAI(
                    api_key=xai_key,
                    base_url="https://api.x.ai/v1"
                )
                self.grok_available = True
                logger.info(f"xAI Grok Provider initialized ({self.grok_model_name}).")
            except Exception as e:
                logger.warning(f"Could not initialize xAI Grok: {e}")

        # 4. Ollama (Local LLM via REST or OpenAI-compatible endpoint)
        self.ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.ollama_model_name = os.environ.get("OLLAMA_MODEL", "llama3")
        # Probe Ollama connectivity with short timeout
        try:
            import httpx
            with httpx.Client(timeout=1.0) as client:
                res = client.get(f"{self.ollama_base_url}/api/tags")
                if res.status_code == 200:
                    self.ollama_available = True
                    logger.info(f"Ollama Local LLM Provider initialized at {self.ollama_base_url} ({self.ollama_model_name}).")
        except Exception:
            # Keep available flag False until explicitly pinged or configured
            pass

    def get_available_providers(self) -> Dict[str, Any]:
        """Returns the real-time status of all integrated LLM providers."""
        preferred = os.environ.get("PREFERRED_LLM_PROVIDER", "auto").lower()
        return {
            "gemini": {
                "available": self.gemini_available,
                "model": getattr(self, "gemini_model_name", "gemini-1.5-pro"),
            },
            "openai": {
                "available": self.openai_available,
                "model": getattr(self, "openai_model_name", "gpt-4o-mini"),
            },
            "grok": {
                "available": self.grok_available,
                "model": getattr(self, "grok_model_name", "grok-2-latest"),
            },
            "ollama": {
                "available": self.ollama_available,
                "model": getattr(self, "ollama_model_name", "llama3"),
                "base_url": getattr(self, "ollama_base_url", "http://localhost:11434"),
            },
            "preferred_provider": preferred,
            "last_used_provider": self.last_provider_used,
        }

    def _determine_provider_order(self, preferred_provider: Optional[str] = None) -> List[str]:
        """Resolves execution priority order based on config and runtime availability."""
        pref = (preferred_provider or os.environ.get("PREFERRED_LLM_PROVIDER", "auto")).lower()
        all_providers = ["gemini", "openai", "grok", "ollama"]

        if pref in all_providers:
            # Place preferred first, followed by others
            order = [pref] + [p for p in all_providers if p != pref]
        else:
            order = all_providers

        return order

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        preferred_provider: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Invokes LLM with system and user prompts, expecting a JSON response.
        Uses the selected provider and returns None when it cannot produce valid JSON.
        Returns parsed dictionary, or None if all providers fail or are unconfigured.
        """
        pref = (preferred_provider or os.environ.get("PREFERRED_LLM_PROVIDER", "auto")).lower()
        provider_order = self._determine_provider_order(preferred_provider)

        for provider in provider_order:
            if provider == "gemini" and self.gemini_available:
                result = self._call_gemini_json(system_prompt, user_prompt, temperature)
                if result is not None:
                    self.last_provider_used = f"Google Gemini ({self.gemini_model_name})"
                    return result
                return None

            elif provider == "openai" and self.openai_available:
                result = self._call_openai_json(system_prompt, user_prompt, temperature)
                if result is not None:
                    self.last_provider_used = f"OpenAI ({self.openai_model_name})"
                    return result
                return None

            elif provider == "grok" and self.grok_available:
                result = self._call_grok_json(system_prompt, user_prompt, temperature)
                if result is not None:
                    self.last_provider_used = f"xAI Grok ({self.grok_model_name})"
                    return result
                return None

            elif provider == "ollama" and (self.ollama_available or pref == "ollama"):
                result = self._call_ollama_json(system_prompt, user_prompt, temperature)
                if result is not None:
                    self.last_provider_used = f"Local Ollama ({self.ollama_model_name})"
                    return result
                return None

        return None

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        preferred_provider: Optional[str] = None,
    ) -> Optional[str]:
        """
        Invokes LLM expecting a plain text response with cascading multi-provider fallback.
        """
        pref = (preferred_provider or os.environ.get("PREFERRED_LLM_PROVIDER", "auto")).lower()
        provider_order = self._determine_provider_order(preferred_provider)

        for provider in provider_order:
            if provider == "gemini" and self.gemini_available:
                try:
                    full_prompt = f"{system_prompt}\n\nUSER PROMPT:\n{user_prompt}"
                    res = self.gemini_client.models.generate_content(
                        model=self.gemini_model_name,
                        contents=full_prompt,
                        config={"temperature": temperature},
                    )
                    if res and res.text:
                        self.last_provider_used = f"Google Gemini ({self.gemini_model_name})"
                        return res.text.strip()
                except Exception as e:
                    logger.warning(f"Gemini text generation failed: {e}. Cascading...")

            elif provider == "openai" and self.openai_available:
                try:
                    res = self.openai_client.chat.completions.create(
                        model=self.openai_model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=temperature,
                    )
                    text = res.choices[0].message.content
                    if text:
                        self.last_provider_used = f"OpenAI ({self.openai_model_name})"
                        return text.strip()
                except Exception as e:
                    logger.warning(f"OpenAI text generation failed: {e}. Cascading...")

            elif provider == "grok" and self.grok_available:
                try:
                    res = self.grok_client.chat.completions.create(
                        model=self.grok_model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=temperature,
                    )
                    text = res.choices[0].message.content
                    if text:
                        self.last_provider_used = f"xAI Grok ({self.grok_model_name})"
                        return text.strip()
                except Exception as e:
                    logger.warning(f"xAI Grok text generation failed: {e}. Cascading...")

            elif provider == "ollama" and (self.ollama_available or pref == "ollama"):
                try:
                    import httpx
                    payload = {
                        "model": self.ollama_model_name,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "stream": False,
                        "options": {"temperature": temperature}
                    }
                    res = httpx.post(f"{self.ollama_base_url}/api/chat", json=payload, timeout=120.0)
                    if res.status_code == 200:
                        data = res.json()
                        text = data.get("message", {}).get("content", "")
                        if text:
                            self.last_provider_used = f"Local Ollama ({self.ollama_model_name})"
                            return text.strip()
                except Exception as e:
                    logger.warning(f"Ollama text generation failed: {e}. Cascading...")

        return None

    # --- PROVIDER IMPLEMENTATIONS FOR JSON MODE ---

    def _call_gemini_json(self, system_prompt: str, user_prompt: str, temperature: float) -> Optional[Dict[str, Any]]:
        try:
            full_prompt = f"{system_prompt}\n\nUSER DATA:\n{user_prompt}\n\nReturn ONLY a valid JSON object."
            response = self.gemini_client.models.generate_content(
                model=self.gemini_model_name,
                contents=full_prompt,
                config={
                    "temperature": temperature,
                    "response_mime_type": "application/json",
                },
            )
            return self._parse_json(response.text)
        except Exception as e:
            logger.warning(f"Gemini generation failed: {e}. Attempting fallback.")
            return None

    def _call_openai_json(self, system_prompt: str, user_prompt: str, temperature: float) -> Optional[Dict[str, Any]]:
        try:
            response = self.openai_client.chat.completions.create(
                model=self.openai_model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            text = response.choices[0].message.content
            return self._parse_json(text)
        except Exception as e:
            logger.warning(f"OpenAI generation failed: {e}. Attempting fallback.")
            return None

    def _call_grok_json(self, system_prompt: str, user_prompt: str, temperature: float) -> Optional[Dict[str, Any]]:
        try:
            # xAI Grok supports OpenAI-compatible chat completions
            response = self.grok_client.chat.completions.create(
                model=self.grok_model_name,
                messages=[
                    {"role": "system", "content": f"{system_prompt}\nYou MUST output strictly a valid JSON object without surrounding prose."},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
            )
            text = response.choices[0].message.content
            return self._parse_json(text)
        except Exception as e:
            logger.warning(f"xAI Grok generation failed: {e}. Attempting fallback.")
            return None

    def _call_ollama_json(self, system_prompt: str, user_prompt: str, temperature: float) -> Optional[Dict[str, Any]]:
        try:
            import httpx
            payload = {
                "model": self.ollama_model_name,
                "messages": [
                    {"role": "system", "content": f"{system_prompt}\nReturn strictly a valid JSON object."},
                    {"role": "user", "content": user_prompt}
                ],
                "format": "json",
                "stream": False,
                "think": False,
                "options": {"temperature": temperature}
            }
            res = httpx.post(f"{self.ollama_base_url}/api/chat", json=payload, timeout=180.0)
            if res.status_code == 200:
                data = res.json()
                text = data.get("message", {}).get("content", "")
                parsed = self._parse_json(text)
                if parsed:
                    self.ollama_available = True
                    return parsed
        except Exception as e:
            logger.warning(f"Local Ollama generation failed: {e}. Attempting fallback.")
        return None

    def _parse_json(self, text: Optional[str]) -> Optional[Dict[str, Any]]:
        """Extracts and parses JSON from raw LLM output with fence cleanup."""
        if not text:
            return None
        text = text.strip()
        # Clean markdown code blocks ```json ... ```
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
            text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try finding first { and last }
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except Exception:
                    pass
            logger.warning(f"Failed to parse LLM JSON output: {text[:200]}")
            return None


llm_client = LLMClient()
