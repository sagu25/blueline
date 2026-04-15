"""
LLM Client — supports Azure OpenAI (primary) and Anthropic Claude (fallback).

Priority:
  1. Azure OpenAI  → if AZURE_OPENAI_ENDPOINT is set  (recommended for company use)
  2. Anthropic     → if ANTHROPIC_API_KEY is set       (personal / external use only)
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _is_azure_configured() -> bool:
    return bool(
        os.getenv("AZURE_OPENAI_ENDPOINT") and
        os.getenv("AZURE_OPENAI_API_KEY") and
        os.getenv("AZURE_OPENAI_DEPLOYMENT")
    )


def _is_anthropic_configured() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def get_active_provider() -> str:
    """Returns which LLM provider is currently active."""
    if _is_azure_configured():
        return "azure_openai"
    if _is_anthropic_configured():
        return "anthropic"
    return "none"


def call_claude(system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
    """
    Unified LLM call. Automatically uses Azure OpenAI or Anthropic
    depending on what is configured in .env.
    """
    provider = get_active_provider()

    if provider == "azure_openai":
        return _call_azure_openai(system_prompt, user_message, max_tokens)
    elif provider == "anthropic":
        return _call_anthropic(system_prompt, user_message, max_tokens)
    else:
        raise ValueError(
            "No LLM provider configured.\n"
            "Set AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY + AZURE_OPENAI_DEPLOYMENT in .env\n"
            "OR set ANTHROPIC_API_KEY in .env"
        )


# ── Azure OpenAI ────────────────────────────────────────────────────────────
def _call_azure_openai(system_prompt: str, user_message: str, max_tokens: int) -> str:
    """
    Calls Azure OpenAI (GPT-4o or any deployed model).
    Data stays within your company's Azure tenant.
    """
    from openai import AzureOpenAI

    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
    )

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        max_tokens=max_tokens,
        temperature=0.1       # low temperature = more consistent, deterministic output
    )

    return response.choices[0].message.content


# ── Anthropic Claude ────────────────────────────────────────────────────────
def _call_anthropic(system_prompt: str, user_message: str, max_tokens: int) -> str:
    """
    Calls Anthropic Claude API directly.
    NOTE: Data is sent to Anthropic's external servers.
    Only use if your company policy allows it.
    """
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}
            }
        ],
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    return response.content[0].text
