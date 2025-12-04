"""
Backstory-related services.
"""

import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = None

def get_client():
    """Get or create OpenAI client."""
    global client
    if client is None:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        client = OpenAI(api_key=OPENAI_API_KEY)
    return client

PROMPT = (
    "You are generating a short, mistaken backstory for a police composite sketch. "
    "The photo provided is the 'suspect', but the story must be intentionally wrong "
    "and slightly humorous. Keep it to 2–3 sentences. Avoid anything offensive, "
    "racial, political, or violent. Make it sound like a confused witness "
    "describing the wrong person."
)

def generate_backstory_from_bytes(image_bytes: bytes) -> str:
    img_b64 = base64.b64encode(image_bytes).decode("utf-8")
    client = get_client()

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a creative but safe backstory generator.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        },
                    },
                ],
            },
        ],
        max_tokens=200,
    )
    return resp.choices[0].message.content.strip()

