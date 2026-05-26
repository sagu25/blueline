"""
LLM Client — Azure OpenAI only.
Data stays within the company's Azure tenant.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_active_provider() -> str:
    """Returns 'azure_openai' if configured, else 'none'."""
    if (
        os.getenv("AZURE_OPENAI_ENDPOINT") and
        os.getenv("AZURE_OPENAI_API_KEY") and
        os.getenv("AZURE_OPENAI_DEPLOYMENT")
    ):
        return "azure_openai"
    return "none"


def call_claude(system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
    """
    Calls Azure OpenAI. Raises if credentials are not configured in .env.
    """
    if get_active_provider() != "azure_openai":
        raise ValueError(
            "Azure OpenAI not configured.\n"
            "Set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and "
            "AZURE_OPENAI_DEPLOYMENT in your .env file."
        )

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
        temperature=0.1
    )

    return response.choices[0].message.content
