"""
The 25 models: provider, API model identifier and whether the reasoning mode was on.

Two model sets correspond to the two designs of the study (data_collection/designs.py):
  COMPLETE_DESIGN_MODELS  16 models, run at five trials per cell with strategy-play, self-play and full cross-play
  FRONTIER_DESIGN_MODELS   9 frontier models, run at one trial per cell with strategy-play and self-play

Providers: "anthropic" and "openai" are the developers' APIs, "google_vertex" is Google Vertex AI, and "openrouter" is
OpenRouter (an OpenAI-compatible API that serves the other models).
"""

ALL_MODELS = {
    # Anthropic
    "claude-haiku-4.5":             {"provider": "anthropic", "model_id": "claude-haiku-4-5-20251001",  "thinking": False},
    "claude-haiku-4.5-thinking":    {"provider": "anthropic", "model_id": "claude-haiku-4-5-20251001",  "thinking": True},
    "claude-sonnet-4.5":            {"provider": "anthropic", "model_id": "claude-sonnet-4-5-20250929", "thinking": False},
    "claude-opus-4.5":              {"provider": "anthropic", "model_id": "claude-opus-4-5",            "thinking": False},
    "claude-sonnet-4.6":            {"provider": "anthropic", "model_id": "claude-sonnet-4-6",          "thinking": False},
    "claude-opus-4.6":              {"provider": "anthropic", "model_id": "claude-opus-4-6",            "thinking": False},
    # OpenAI
    "gpt-4o-mini":                  {"provider": "openai", "model_id": "gpt-4o-mini",                  "thinking": False},
    "gpt-4.1":                      {"provider": "openai", "model_id": "gpt-4.1",                      "thinking": False},
    "gpt-4.1-mini":                 {"provider": "openai", "model_id": "gpt-4.1-mini",                 "thinking": False},
    "gpt-4.1-nano":                 {"provider": "openai", "model_id": "gpt-4.1-nano",                 "thinking": False},
    "gpt-5-mini":                   {"provider": "openai", "model_id": "gpt-5-mini",                   "thinking": False},
    "gpt-5-nano":                   {"provider": "openai", "model_id": "gpt-5-nano",                   "thinking": False},
    "gpt-5.3":                      {"provider": "openai", "model_id": "gpt-5.3-chat-latest",          "thinking": False},
    "gpt-5.4":                      {"provider": "openai", "model_id": "gpt-5.4",                      "thinking": False},
    # Google (Gemini 2.0 to 3 Flash through OpenRouter, Gemini 3 Pro and 3.1 Pro through Vertex AI). The stored costs
    # of the Gemini Flash trials match Google's own model identifiers, so these models may have used Google's API;
    # the trial files do not name the route. Gemini 2.5 Flash (Thinking) has the same settings here as Gemini 2.5
    # Flash, although only its trials carry reasoning text, so its thinking setting at collection is not recorded.
    "gemini-2.0-flash":             {"provider": "openrouter", "model_id": "google/gemini-2.0-flash-001",    "thinking": False},
    "gemini-2.5-flash":             {"provider": "openrouter", "model_id": "google/gemini-2.5-flash",        "thinking": False},
    "gemini-2.5-flash-thinking":    {"provider": "openrouter", "model_id": "google/gemini-2.5-flash",        "thinking": False},
    "gemini-3-flash":               {"provider": "openrouter", "model_id": "google/gemini-3-flash-preview",  "thinking": False},
    "gemini-3-pro":                 {"provider": "google_vertex", "model_id": "gemini-3-pro-preview",    "thinking": True},
    "gemini-3.1-pro":               {"provider": "google_vertex", "model_id": "gemini-3.1-pro-preview",  "thinking": True},
    # DeepSeek, Meta, Mistral and Alibaba (through OpenRouter)
    "llama-3.3-70b":                {"provider": "openrouter", "model_id": "meta-llama/llama-3.3-70b-instruct",    "thinking": False},
    "deepseek-r1":                  {"provider": "openrouter", "model_id": "deepseek/deepseek-r1",                 "thinking": False},
    "deepseek-v3":                  {"provider": "openrouter", "model_id": "deepseek/deepseek-chat-v3-0324",       "thinking": False},
    "ministral-14b":                {"provider": "openrouter", "model_id": "mistralai/ministral-14b-2512",        "thinking": False},
    "qwen3.5-flash":                {"provider": "openrouter", "model_id": "qwen/qwen3.5-flash-02-23",            "thinking": False},
}

# The complete design: 16 models, all 38 games, five trials per cell, strategy-play, self-play and full cross-play
COMPLETE_DESIGN_MODELS = {k: ALL_MODELS[k] for k in [
    "gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-flash-thinking", "gemini-3-flash",
    "claude-haiku-4.5", "claude-haiku-4.5-thinking",
    "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4o-mini", "gpt-5-mini", "gpt-5-nano",
    "llama-3.3-70b", "deepseek-v3", "deepseek-r1", "ministral-14b", "qwen3.5-flash",
]}

# The frontier design: 9 frontier models, all 38 games, one trial per cell, strategy-play and self-play
FRONTIER_DESIGN_MODELS = {k: ALL_MODELS[k] for k in [
    "claude-opus-4.5", "claude-opus-4.6", "claude-sonnet-4.5", "claude-sonnet-4.6",
    "gemini-3-pro", "gemini-3.1-pro",
    "gpt-4.1", "gpt-5.3", "gpt-5.4",
]}

MODEL_SETS = {
    "complete": COMPLETE_DESIGN_MODELS,
    "frontier": FRONTIER_DESIGN_MODELS,
    "all": ALL_MODELS,
}


def get_model_set(name: str) -> dict:
    """Get a model set by name."""
    if name not in MODEL_SETS:
        raise ValueError(f"Unknown model set: {name}. "
                         f"Available: {list(MODEL_SETS.keys())}")
    return MODEL_SETS[name]
