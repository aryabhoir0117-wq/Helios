import os
import httpx
from dotenv import load_dotenv 

load_dotenv ()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def explain_root_cause(title: str, root_cause: str) -> str:
    prompt = (
        f"An incident was detected: '{title}'. "
        f"The rule-based root cause analysis found: '{root_cause}'. "
        f"Write a single 2-3 sentence plain-English explanation for a non-technical on-call viewer. "
        f"Output only the explanation itself, no preamble, no alternate versions."
    )
    try:
        return await _call_groq(prompt)
    except Exception as e:
        print(f"⚠️ Groq failed ({e}), falling back to Gemini")
        try:
            return await _call_gemini(prompt)
        except Exception as e2:
            print(f"⚠️ Gemini also failed ({e2})")
            raise


async def _call_groq(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def _call_gemini(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
        )
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()