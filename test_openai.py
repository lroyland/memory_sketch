from dotenv import load_dotenv
load_dotenv()
import base64, os
from openai import OpenAI

print('openai?', bool(os.getenv('OPENAI_API_KEY')))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("test_selfie.png", "rb") as f:
    img_bytes = f.read()

img_b64 = base64.b64encode(img_bytes).decode("utf-8")

PROMPT = (
    "You are generating a short, mistaken backstory for a police composite sketch. "
    "The photo provided is the 'suspect', but the story must be intentionally wrong "
    "and slightly humorous. Keep it to 2–3 sentences. Avoid anything offensive, "
    "racial, political, or violent. Make it sound like a confused witness "
    "describing the wrong person."
)

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
print(resp.choices[0].message.content)
