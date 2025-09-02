import os
from openai import OpenAI
from backend.app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_summary(transcript_text: str) -> str:
    """
    Generate a summary of a meeting transcript using OpenAI GPT model.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",   # cheaper + fast
        messages=[
            {"role": "system", "content": "You are an AI that summarizes meeting transcripts."},
            {"role": "user", "content": transcript_text}
        ],
        max_tokens=500  # limit summary length
    )
    return response.choices[0].message.content.strip()
