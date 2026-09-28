"""
API calls to the model providers: Anthropic, OpenAI, OpenRouter and Google Vertex AI.

Every caller takes a system prompt and a user message and returns a dict with the reply text, the thinking or
reasoning text when the provider returns it, and the token counts. Keys are read from the environment (or from a
file data_collection/.env with KEY=value lines): ANTHROPIC_API_KEY, OPENAI_API_KEY, OPENROUTER_API_KEY, and for
Vertex AI a service account key file named by GOOGLE_APPLICATION_CREDENTIALS, the project in GOOGLE_CLOUD_PROJECT and
optionally the region in VERTEX_LOCATION.
"""

import os
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAX_RETRIES = 4
API_CALL_DELAY = 3.0  # pause between calls for providers not listed below (Vertex AI)

# Pause between calls, per provider
PROVIDER_DELAYS = {
    "anthropic": 0.1,
    "openai": 0.1,
    "openrouter": 0.1,
}


def get_delay(provider: str) -> float:
    """Get the pause between API calls for a provider."""
    return PROVIDER_DELAYS.get(provider, API_CALL_DELAY)


def load_env():
    """Load API keys from data_collection/.env (KEY=value lines), if the file exists."""
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()


def check_providers() -> set[str]:
    """Check which API providers have keys configured. Returns set of provider names."""
    available = set()
    if os.environ.get("ANTHROPIC_API_KEY"):
        available.add("anthropic")
    if os.environ.get("OPENAI_API_KEY"):
        available.add("openai")
    if os.environ.get("OPENROUTER_API_KEY"):
        available.add("openrouter")
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        available.add("google_vertex")
    return available


# ---------------------------------------------------------------------------
# API callers (text only)
# ---------------------------------------------------------------------------

def call_anthropic(model_id: str, system_prompt: str, user_message: str,
                   thinking: bool = False, max_tokens: int = 1024,
                   temperature: float = 1.0) -> dict:
    """Send text prompt to Anthropic API. Returns dict with text, tokens."""
    import anthropic
    client = anthropic.Anthropic()

    messages = [{"role": "user", "content": user_message}]

    kwargs = {
        "model": model_id,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system_prompt:
        kwargs["system"] = system_prompt
    # Anthropic does not support temperature with extended thinking
    if thinking:
        kwargs["thinking"] = {"type": "enabled", "budget_tokens": 4096}
        kwargs["max_tokens"] = 8192
    else:
        kwargs["temperature"] = temperature

    response = client.messages.create(**kwargs)

    text = ""
    thinking_text = ""
    for block in response.content:
        if block.type == "text":
            text = block.text
        elif block.type == "thinking":
            thinking_text = block.thinking

    return {
        "text": text,
        "thinking": thinking_text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "model_id": model_id,
    }


def call_openai(model_id: str, system_prompt: str, user_message: str,
                thinking: bool = False, max_tokens: int = 1024,
                temperature: float = 1.0) -> dict:
    """Send text prompt to OpenAI API. Returns dict with text, tokens."""
    import openai
    client = openai.OpenAI()

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_message})

    # Responses API path for models with the reasoning mode on: the Responses
    # API exposes reasoning summaries that Chat Completions does not.
    if thinking:
        input_msgs = []
        if system_prompt:
            input_msgs.append({"role": "system", "content": system_prompt})
        input_msgs.append({"role": "user", "content": user_message})

        resp_kwargs = {
            "model": model_id,
            "input": input_msgs,
            "temperature": temperature,
        }
        if thinking:
            resp_kwargs["reasoning"] = {"effort": "medium", "summary": "auto"}

        response = client.responses.create(**resp_kwargs)

        # Extract text and reasoning summary
        text = ""
        thinking_text = ""
        for item in response.output:
            item_type = getattr(item, "type", "")
            if item_type == "reasoning":
                summaries = getattr(item, "summary", None)
                if summaries:
                    parts = []
                    for s in summaries:
                        s_type = getattr(s, "type", "")
                        if s_type == "summary_text":
                            parts.append(getattr(s, "text", ""))
                    if parts:
                        thinking_text = "\n".join(parts)
            elif item_type == "message":
                content = getattr(item, "content", [])
                for c in content:
                    c_type = getattr(c, "type", "")
                    if c_type == "output_text":
                        text = getattr(c, "text", "")

        input_tokens = getattr(response.usage, "input_tokens", 0) or 0
        output_tokens = getattr(response.usage, "output_tokens", 0) or 0
        return {
            "text": text or (response.output_text or ""),
            "thinking": thinking_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "model_id": model_id,
        }

    # Chat Completions path for non-thinking models
    kwargs = {"model": model_id, "messages": messages, "temperature": temperature}

    # Newer models require max_completion_tokens
    uses_new_param = model_id in (
        "gpt-5-mini", "gpt-5-nano", "gpt-5.3-chat-latest", "gpt-5.4",
    )
    if uses_new_param:
        kwargs["max_completion_tokens"] = max_tokens * 2
    else:
        kwargs["max_tokens"] = max_tokens

    response = client.chat.completions.create(**kwargs)

    input_tokens = getattr(response.usage, "prompt_tokens", 0) or 0
    output_tokens = getattr(response.usage, "completion_tokens", 0) or 0

    # Capture reasoning_tokens count if available
    reasoning_tokens = 0
    comp_details = getattr(response.usage, "completion_tokens_details", None)
    if comp_details:
        reasoning_tokens = getattr(comp_details, "reasoning_tokens", 0) or 0

    return {
        "text": response.choices[0].message.content or "",
        "thinking": "",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "reasoning_tokens": reasoning_tokens,
        "model_id": model_id,
    }


def _extract_google_parts(response):
    """Extract text and thinking parts from a Google GenAI response."""
    text = ""
    thinking_text = ""
    try:
        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if not part.text:
                    continue
                if getattr(part, "thought", False):
                    thinking_text += part.text + "\n"
                else:
                    text += part.text
    except (AttributeError, IndexError):
        pass

    if not text:
        try:
            text = response.text if response.text else ""
        except Exception:
            text = ""

    return text, thinking_text.strip()


def _google_thinking_config(types, model_id: str, thinking: bool):
    """Build ThinkingConfig for a Google model."""
    tc_kwargs = {}
    include = thinking  # only include thoughts when thinking is on
    if model_id.startswith("gemini-3"):
        is_pro = "pro" in model_id
        level = "high" if thinking else ("low" if is_pro else "minimal")
        tc_kwargs["thinking_level"] = level
    elif model_id.startswith("gemini-2.5"):
        is_pro = "pro" in model_id
        is_lite = "lite" in model_id
        if thinking:
            tc_kwargs["thinking_budget"] = -1
        elif is_pro:
            tc_kwargs["thinking_budget"] = 128
        elif not is_lite:
            tc_kwargs["thinking_budget"] = 0
            include = False  # no thoughts when budget=0
        else:
            return None  # lite: no thinking config needed
    else:
        return None  # other models: no thinking config

    if include:
        tc_kwargs["include_thoughts"] = True
    return types.ThinkingConfig(**tc_kwargs)


# ---------------------------------------------------------------------------
# Google Vertex AI (service account credentials)
# ---------------------------------------------------------------------------

# One Vertex AI client per location
_vertex_sa_clients: dict[str, object] = {}
_vertex_sa_credentials = None

def _get_vertex_location(model_id: str) -> str:
    """Determine Vertex AI location for a model.
    Preview models (gemini-3.x) require the 'global' endpoint.
    Stable models use the configured region (default: us-east1).
    """
    if "preview" in model_id:
        return "global"
    return os.environ.get("VERTEX_LOCATION", "us-east1")

def _get_vertex_sa_client(location: str = None):
    """Get or create a Vertex AI client for a given location."""
    global _vertex_sa_credentials
    if location is None:
        location = os.environ.get("VERTEX_LOCATION", "us-east1")

    if location in _vertex_sa_clients:
        return _vertex_sa_clients[location]

    from google import genai
    from google.oauth2 import service_account

    sa_key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not sa_key_path or not Path(sa_key_path).exists():
        raise FileNotFoundError("Set GOOGLE_APPLICATION_CREDENTIALS to a Vertex AI service account key file")

    if _vertex_sa_credentials is None:
        _vertex_sa_credentials = service_account.Credentials.from_service_account_file(
            str(sa_key_path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

    client = genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=location,
        credentials=_vertex_sa_credentials,
    )
    _vertex_sa_clients[location] = client
    return client


def call_google_vertex(model_id: str, system_prompt: str, user_message: str,
                       thinking: bool = False, max_tokens: int = 1024,
                       temperature: float = 1.0) -> dict:
    """Send text prompt to Google Vertex AI (service account credentials)."""
    from google.genai import types

    location = _get_vertex_location(model_id)
    client = _get_vertex_sa_client(location=location)

    config_kwargs = {"max_output_tokens": max_tokens, "temperature": temperature}

    # System instruction (Gemma models don't support developer instructions)
    is_gemma = model_id.startswith("gemma")
    if system_prompt and not is_gemma:
        config_kwargs["system_instruction"] = system_prompt
    elif system_prompt and is_gemma:
        user_message = f"{system_prompt}\n\n{user_message}"

    # Thinking configuration (shared helper)
    tc = _google_thinking_config(types, model_id, thinking)
    if tc is not None:
        config_kwargs["thinking_config"] = tc

    response = client.models.generate_content(
        model=model_id,
        contents=[user_message],
        config=types.GenerateContentConfig(**config_kwargs),
    )

    input_tokens = 0
    output_tokens = 0
    if response.usage_metadata:
        input_tokens = response.usage_metadata.prompt_token_count or 0
        output_tokens = response.usage_metadata.candidates_token_count or 0

    text, thinking_text = _extract_google_parts(response)

    return {
        "text": text,
        "thinking": thinking_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "model_id": model_id,
    }


# ---------------------------------------------------------------------------
# OpenRouter (OpenAI-compatible API)
# ---------------------------------------------------------------------------

def call_openrouter(model_id: str, system_prompt: str, user_message: str,
                    thinking: bool = False, max_tokens: int = 1024,
                    temperature: float = 1.0) -> dict:
    """Send text prompt to OpenRouter API. Returns dict with text, tokens.

    For reasoning models (DeepSeek-R1, etc.), captures the reasoning text
    from the message's `reasoning` or `reasoning_content` field.
    """
    import openai
    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
    )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_message})

    # Some newer models on OpenRouter require max_completion_tokens
    _new_token_models = ("gpt-5.3", "gpt-5.4", "gemini-3-pro", "gemini-3.1")
    use_new = any(tag in model_id for tag in _new_token_models)
    token_kwarg = {"max_completion_tokens": max_tokens * 2} if use_new else {"max_tokens": max_tokens}

    response = client.chat.completions.create(
        model=model_id,
        messages=messages,
        temperature=temperature,
        **token_kwarg,
    )

    input_tokens = getattr(response.usage, "prompt_tokens", 0) or 0
    output_tokens = getattr(response.usage, "completion_tokens", 0) or 0

    msg = response.choices[0].message
    text = msg.content or ""

    # Capture the reasoning text from OpenRouter/DeepSeek models
    thinking_text = ""
    # OpenRouter uses `reasoning` field
    reasoning = getattr(msg, "reasoning", None)
    if reasoning:
        thinking_text = reasoning
    # DeepSeek native uses `reasoning_content`
    if not thinking_text:
        reasoning_content = getattr(msg, "reasoning_content", None)
        if reasoning_content:
            thinking_text = reasoning_content

    return {
        "text": text,
        "thinking": thinking_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "model_id": model_id,
    }


# ---------------------------------------------------------------------------
# Provider dispatch
# ---------------------------------------------------------------------------

PROVIDERS = {
    "anthropic": call_anthropic,
    "openai": call_openai,
    "google_vertex": call_google_vertex,
    "openrouter": call_openrouter,
}


def call_model(model_key: str, model_cfg: dict,
               system_prompt: str, user_message: str,
               max_tokens: int = 1024, temperature: float = 1.0) -> dict:
    """
    Dispatch to the provider of the model.
    Returns dict with: text, thinking, input_tokens, output_tokens, model_id
    """
    caller = PROVIDERS[model_cfg["provider"]]
    return caller(
        model_id=model_cfg["model_id"],
        system_prompt=system_prompt,
        user_message=user_message,
        thinking=model_cfg.get("thinking", False),
        max_tokens=max_tokens,
        temperature=temperature,
    )


# ---------------------------------------------------------------------------
# Retry logic
# ---------------------------------------------------------------------------

def call_with_retry(caller_fn, max_retries: int = MAX_RETRIES, **kwargs) -> dict:
    """Call API with exponential backoff on rate limit / overloaded errors."""
    for attempt in range(max_retries + 1):
        try:
            return caller_fn(**kwargs)
        except Exception as e:
            error_str = str(e).lower()
            is_retryable = any(w in error_str for w in [
                "rate", "429", "overloaded", "529", "too many", "quota",
                "resource_exhausted", "capacity", "503", "could not finish",
            ])
            if is_retryable and attempt < max_retries:
                wait = min(2 ** attempt * 2, 30)
                print(f"    [retry] {type(e).__name__}, waiting {wait}s "
                      f"(attempt {attempt+1}/{max_retries})...")
                time.sleep(wait)
            else:
                raise
    raise Exception(f"Failed after {max_retries} retries")


def call_model_with_retry(model_key: str, model_cfg: dict,
                           system_prompt: str, user_message: str,
                           max_tokens: int = 1024,
                           temperature: float = 1.0) -> dict:
    """Call model API with retry logic."""
    return call_with_retry(
        call_model,
        model_key=model_key,
        model_cfg=model_cfg,
        system_prompt=system_prompt,
        user_message=user_message,
        max_tokens=max_tokens,
        temperature=temperature,
    )
