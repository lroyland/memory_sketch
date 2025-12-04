import os
import base64
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def generate_backstory_from_bytes(image_bytes: bytes) -> str:
    """
    Generate a short, playful, entirely fictional 'memory' style story
    based on the vibe of the person in the image.

    The story MUST NOT identify the person, guess real attributes,
    or say it's analyzing an image. It's just an invented anecdote.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")

    img_b64 = base64.b64encode(image_bytes).decode("utf-8")
    image_url = f"data:image/png;base64,{img_b64}"

    system_prompt = (
        "You are writing playful, entirely fictional 'memory' snippets for an art project "
        "called 'Memory Sketch'. Each snippet pretends the narrator vaguely remembers having "
        "met the person in the image once before.\n\n"
        "Rules:\n"
        "- This is PURE FICTION. Do not identify the real person or claim to know who they are.\n"
        "- Do NOT guess or state real-world personal attributes like name, ethnicity, nationality, "
        "religion, or specific job title.\n"
        "- Do NOT say you are an AI or refer to 'the image' or 'this photo'.\n"
        "- Speak in first person as if you are the narrator recalling a brief encounter.\n"
        "- Keep it light, human, and a bit impressionistic.\n"
        "- 3–5 sentences max.\n"
        "- It's okay if details are a little off; that's the concept of the project.\n"
    )

    user_text = (
        "Create a short, fictional 'I vaguely remember meeting you' story.\n\n"
        "Write 3–5 sentences in the first person. Imagine I met this person once at a festival, "
        "gallery opening, or coffee shop and I'm trying to describe what I remember about the vibe "
        "of that encounter.\n\n"
        "Do NOT try to identify who they are. Do NOT mention that you are looking at an image. "
        "Just tell the little memory as if it were real, but keep it obviously light and anecdotal."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            },
        ],
        max_tokens=220,
        temperature=0.9,
    )

    content = response.choices[0].message.content
    # Some SDK versions return a list of segments; normalize to string
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content)
    return content
