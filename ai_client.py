import os
import json
import base64
import re
from typing import Optional

PROVIDER = os.environ.get("AI_PROVIDER", "gemini")


def extract_document_data(image_bytes: bytes, schema: dict, mime_type: str = "image/jpeg") -> dict:
    """
    Main entry point. Swap AI_PROVIDER env var to change backend.
    Supported: gemini (free), claude, openai
    """
    if PROVIDER == "gemini":
        return _gemini_extract(image_bytes, schema, mime_type)
    elif PROVIDER == "claude":
        return _claude_extract(image_bytes, schema, mime_type)
    elif PROVIDER == "openai":
        return _openai_extract(image_bytes, schema, mime_type)
    else:
        raise ValueError(f"Unknown AI_PROVIDER: {PROVIDER}")


def _build_prompt(schema: dict) -> str:
    fields_desc = "\n".join(
        f'- "{k}": {v}' for k, v in schema["fields"].items()
    )
    return f"""You are a document data extraction assistant.
Extract the following fields from the document image and return ONLY a valid JSON object.
Do not include any explanation, markdown, or extra text — just the raw JSON.

Fields to extract:
{fields_desc}

If a field is not found or unclear, use null for its value.
Preserve original formatting for values (dates, currency symbols, etc.)."""


def _clean_json(raw: str) -> dict:
    """Strip markdown fences and parse JSON safely."""
    cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
    return json.loads(cleaned)


# ── GEMINI (free tier) ──────────────────────────────────────────────────────
def _gemini_extract(image_bytes: bytes, schema: dict, mime_type: str) -> dict:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            _build_prompt(schema)
        ]
    )
    return _clean_json(response.text)

# ── CLAUDE (paid — swap in when client is paying) ──────────────────────────
def _claude_extract(image_bytes: bytes, schema: dict, mime_type: str) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": mime_type, "data": b64}},
                {"type": "text", "text": _build_prompt(schema)}
            ]
        }]
    )
    return _clean_json(message.content[0].text)


# ── OPENAI (paid — swap in when client is paying) ──────────────────────────
def _openai_extract(image_bytes: bytes, schema: dict, mime_type: str) -> dict:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": _build_prompt(schema)}
            ]
        }],
        max_tokens=1024
    )
    return _clean_json(response.choices[0].message.content)
