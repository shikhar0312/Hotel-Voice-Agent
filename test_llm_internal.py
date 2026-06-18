import os
import asyncio
from livekit.plugins import google
from dotenv import load_dotenv

async def test_llm():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    print(f"Testing Gemini LLM with model: {model}")
    
    try:
        llm = google.LLM(model=model, api_key=api_key)
        # Attempt to generate a small response
        async for part in llm.chat(history=[{"role": "user", "text": "Hello"}]):
             print(f"Received: {part.choices[0].delta.text}")
        print("Success!")
    except Exception as e:
        print(f"Captured Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm())
