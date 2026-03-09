"""
ai_engine.py
Handles AI question answering using Groq API (free tier).

TO SWITCH TO CLAUDE LATER:
    1. pip install anthropic
    2. Replace the `call_llm()` function body with:

        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=system,
            messages=messages,
        )
        return response.content[0].text

    3. Set ANTHROPIC_API_KEY in your .env file instead of GROQ_API_KEY.
"""

import os
import requests
import json
import pandas as pd
from data_processor import get_dataset_summary_text



GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Free Groq model - fast and capable
GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are a supply chain analyst AI assistant. "
    "You have access to order shipment data and your job is to answer operational questions "
    "clearly and accurately.\n\n"
    "When answering:\n"
    "- Be direct and specific. Reference actual numbers from the data.\n"
    "- State the answer first, then provide supporting details.\n"
    "- Use plain text only, no markdown formatting like ** or ##.\n"
    "- Keep answers concise but complete.\n"
    "- If a question cannot be answered from the data, say so clearly."
)


def call_llm(system: str, messages: list) -> str:
    """
    Makes a request to the Groq OpenAI-compatible endpoint.
    All messages should be in {"role": ..., "content": ...} format.
    """
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. "
            "Add it to your .env file or export it as an environment variable."
        )

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "system", "content": system}] + messages,
        "max_tokens": 1000,
        "temperature": 0.3,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        raise RuntimeError(
            f"Groq API error {response.status_code}: {response.text}"
        )

    data = response.json()
    return data["choices"][0]["message"]["content"]


def ask_question(df: pd.DataFrame, user_question: str, chat_history: list) -> str:
    """
    Answer a user question about the supply chain data.

    chat_history: list of {"role": "user"/"assistant", "content": "..."}
    The dataset summary is injected into the current user message only.
    """
    summary = get_dataset_summary_text(df)

    full_user_message = (
        f"Here is the current supply chain dataset summary:\n\n"
        f"{summary}\n\n"
        f"User Question: {user_question}\n\n"
        f"Please analyze the data above and answer the question."
    )

    messages = []
    for entry in chat_history:
        messages.append({"role": entry["role"], "content": entry["content"]})
    messages.append({"role": "user", "content": full_user_message})

    return call_llm(SYSTEM_PROMPT, messages)


def get_ai_insight(df: pd.DataFrame, insight_type: str) -> str:
    """
    Generate a specific type of insight about the dataset.
    insight_type: 'overview' | 'bottlenecks' | 'recommendations'
    """
    prompts = {
        "overview": (
            "Give a brief executive summary of this supply chain data. "
            "Highlight the most important findings in 3 to 4 sentences."
        ),
        "bottlenecks": (
            "Identify the top 2 to 3 operational bottlenecks in this supply chain data. "
            "Be specific about which warehouses or products are underperforming and why."
        ),
        "recommendations": (
            "Based on this supply chain data, provide 3 concrete, actionable recommendations "
            "to improve performance. Number each recommendation."
        ),
    }

    question = prompts.get(insight_type, prompts["overview"])
    summary = get_dataset_summary_text(df)

    prompt = (
        f"Here is the supply chain dataset summary:\n\n"
        f"{summary}\n\n"
        f"{question}"
    )

    return call_llm(SYSTEM_PROMPT, [{"role": "user", "content": prompt}])
