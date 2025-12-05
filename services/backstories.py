import os
import base64
import time
import logging
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)
logger = logging.getLogger(__name__)


async def generate_backstory_from_bytes(image_bytes: bytes) -> str:
    """
    Generate a second-person character profile (700-1000 words) that starts grounded
    and gradually spirals into absurdity, based on the person in the image.
    """
    func_start = time.time()
    logger.info("[BACKSTORY] Starting backstory generation...")
    
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")

    encode_start = time.time()
    img_b64 = base64.b64encode(image_bytes).decode("utf-8")
    image_url = f"data:image/png;base64,{img_b64}"
    encode_time = time.time() - encode_start
    logger.info(f"[BACKSTORY] Base64 encoding: {encode_time:.2f}s")

    system_prompt = (
        "You are an assistant that writes fictional second-person character profiles.\n\n"
        "The user may attach an image as a visual reference for a fictional character.\n"
        "You must ALWAYS treat the person in any image as a completely fictional character,\n"
        "even if the user implies it is them or a real person.\n\n"
        "Rules:\n\n"
        "- Do NOT identify who the person in the image is.\n\n"
        "- Do NOT guess or state their real name, age, location, or any sensitive traits.\n\n"
        "- You may only describe neutral, visible traits (e.g., hair, eyes, facial hair) in a generic way.\n\n"
        "- Do NOT say whether they are a public figure or compare them to a real person.\n\n"
        "- Follow all style and structure instructions given by the user.\n"
    )

    user_text = (
        "You are writing about a fictional character who just happens to look like the person in the attached image.\n\n"
        "Write a second-person character profile about this fictional person.\n\n"
        "Tone: direct, simple, grounded at first, then gradually spiraling into full absurdity.\n\n"
        "Length: 700–1000 words.\n\n"
        "---\n\n"
        "## 1. Opening Requirement\n\n"
        "Start with two or three short sentences.\n\n"
        "First sentence must:\n\n"
        "- Include the word \"that\" to imply personal recall.\n\n"
        "- Contain only factual external identity traits from the image\n\n"
        "  (gender, hair, eye color, approximate outward vibe based on the face).\n\n"
        "- No clothing, posture, gesture, background, or emotion interpretation.\n\n"
        "- No mention of age.\n\n"
        "- Must be plain and non-poetic.\n\n"
        "After the identity facts, you may (optionally) add a \"who…\" clause\n\n"
        "—but only after the identity traits.\n\n"
        "The \"who…\" clause is where invented traits may begin.\n\n"
        "Correct examples:\n\n"
        "Identity-only:\n\n"
        "- \"You're that woman with curly hair.\"\n\n"
        "- \"You're that man with dark eyes.\"\n\n"
        "- \"You're that person with the calm expression.\"\n\n"
        "- \"You're that girl with the soft curls.\"\n\n"
        "Identity → \"who…\" + invented trait:\n\n"
        "- \"You're that woman with curly hair who keeps a dozen notebooks.\"\n\n"
        "- \"You're that man with dark eyes who once tried to repair a toaster with a spoon.\"\n\n"
        "- \"You're that person with the calm expression who always misplaces umbrellas.\"\n\n"
        "- \"You're that girl with the soft curls who collects mismatched teacups.\"\n\n"
        "Second sentence:\n\n"
        "Invent, but keep it normal: work, hobbies, where they live, or what they tend to do.\n\n"
        "It should sound like file data or memory recall, not personality analysis.\n\n"
        "Third sentence:\n\n"
        "Lead naturally into one central focus — a situation, habit, incident, or behavior\n\n"
        "that the entire rest of the profile will develop.\n\n"
        "After this opening, the piece should feel like you are telling the fictional person\n\n"
        "what an internal file or report says about them.\n\n"
        "---\n\n"
        "## 2. Build the Focus\n\n"
        "Expand the central focus with made-up but initially believable details.\n\n"
        "This must be only 1 paragraph.\n\n"
        "- No personality interpretation.\n\n"
        "- No \"you seem like the type…\" language.\n\n"
        "- No astrology-reading style.\n\n"
        "- Keep it concrete, factual, and slightly off.\n\n"
        "- Use plain, clear, easy-to-read language.\n\n"
        "---\n\n"
        "## 3. Escalate\n\n"
        "Develop the focus into one continuous story — not multiple unrelated ones.\n\n"
        "This must be the majority of the profile. A conflict must form and escalate.\n\n"
        "The story should have a beginning, middle, and end.\n\n"
        "You can include:\n\n"
        "- overly specific detail\n\n"
        "- bizarre but human-scale actions\n\n"
        "- procedural notes, timestamps, bureaucratic phrasing\n\n"
        "- overextended beats (conversations/actions that go on too long)\n\n"
        "- lengthy, written-out dialogue passages\n\n"
        "- tangents that follow one train of thought without starting a new storyline\n\n"
        "- moments that suddenly feel like another genre (workplace drama, romance, etc.)\n\n"
        "- absurdity that grows in the spirit of sketch comedy, but always orbiting the same incident\n\n"
        "The escalation should feel like the file is becoming increasingly unhinged\n\n"
        "while remaining matter-of-fact.\n\n"
        "---\n\n"
        "## 4. Close Simply\n\n"
        "End with one clean, short sentence summarizing the overall impression the file gives.\n\n"
        "---\n\n"
        "## Style Rules\n\n"
        "- Use occasional report-language phrases:\n\n"
        "  \"The notes indicate…,\" \"One entry mentions…,\" \"According to the file…\"\n\n"
        "- Do not comment on remembering or reconstructing anything.\n\n"
        "- Keep all phrasing plain, direct, and easy to read.\n\n"
        "- All humor must be deadpan and unacknowledged.\n\n"
        "- You may refer back only to the static identity traits from the opening (hair, eyes, gender).\n\n"
        "- Do NOT reference posture, gesture, clothing, background, setting,\n\n"
        "  or inferred behavior from the image.\n\n"
        "- Treat everything as fictional, even if the image shows a real person.\n"
    )



    api_start = time.time()
    response = await client.chat.completions.create(
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
        max_tokens=2000,  # Reduced from 3000 (target is 700-1000 words ≈ ~1300 tokens)
        temperature=0.8,
    )
    api_time = time.time() - api_start
    logger.info(f"[BACKSTORY] API call (gpt-4o): {api_time:.2f}s")

    content = response.choices[0].message.content
    # Some SDK versions return a list of segments; normalize to string
    if isinstance(content, list):
        result = "".join(part.get("text", "") for part in content)
    else:
        result = content
    
    total_time = time.time() - func_start
    logger.info(f"[BACKSTORY] Total backstory generation: {total_time:.2f}s")
    return result
