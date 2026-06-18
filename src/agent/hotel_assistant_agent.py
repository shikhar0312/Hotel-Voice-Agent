"""
src/agent/hotel_assistant_agent.py
────────────────────────────────────
Main LiveKit Agent for Grandview Hotel.
Kelly — the AI voice assistant.
"""

import logging
import os
from dotenv import load_dotenv

load_dotenv()

from livekit.agents import (
    AgentSession,
    Agent,
    RoomInputOptions,
    WorkerOptions,
    cli,
)
from livekit.plugins import deepgram, silero, google

from src.config.settings import settings
from src.prompts.hotel_assistant_prompt import build_hotel_assistant_prompt

# ── Tool imports ──────────────────────────────────────────────────────────────
from src.tools.booking_worker import check_availability, book_room, cancel_booking
from src.tools.checkin_worker import check_in_guest, get_checkin_status
from src.tools.checkout_worker import checkout_guest, get_bill
from src.tools.room_service import fetch_room_service_menu, place_room_service_order
from src.tools.concierge import fetch_hotel_amenities, fetch_local_recommendations, request_housekeeping
from src.tools.guest_lookup import lookup_guest_by_room, lookup_guest_by_name
from src.tools.hubspot_crm import hubspot_find_contact, hubspot_upsert_contact
from src.tools.call_control import end_call

logger = logging.getLogger(__name__)

# ── Tools list ────────────────────────────────────────────────────────────────
HOTEL_TOOLS = [
    check_availability,
    book_room,
    cancel_booking,
    check_in_guest,
    get_checkin_status,
    checkout_guest,
    get_bill,
    fetch_room_service_menu,
    place_room_service_order,
    fetch_hotel_amenities,
    fetch_local_recommendations,
    request_housekeeping,
    lookup_guest_by_room,
    lookup_guest_by_name,
    hubspot_find_contact,
    hubspot_upsert_contact,
    end_call,
]

# ── HotelAssistant class ──────────────────────────────────────────────────────
class HotelAssistant(Agent):
    """Kelly — Grandview Hotel AI voice assistant."""
    def __init__(self):
        super().__init__(
            instructions=build_hotel_assistant_prompt(),
            tools=HOTEL_TOOLS,
        )

# ── Entrypoint ────────────────────────────────────────────────────────────────
async def entrypoint(ctx):
    logger.info("Kelly agent starting for room: %s", ctx.room.name)

    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
    deepgram_tts = os.getenv("DEEPGRAM_TTS_MODEL", "aura-asteria-en")

    logger.info("Using Gemini model: %s", gemini_model)

    session = AgentSession(
        stt=deepgram.STT(model=settings.DEEPGRAM_STT_MODEL),
        llm=google.LLM(
            model=gemini_model,
            api_key=gemini_key,
        ),
        tts=deepgram.TTS(model=deepgram_tts),
        vad=silero.VAD.load(),
    )

    await session.start(
        room=ctx.room,
        agent=HotelAssistant(),
        room_input_options=RoomInputOptions(),
    )

    await session.generate_reply(
        instructions="Greet the guest warmly and ask how you can help them today."
    )

# ── Server + CLI ──────────────────────────────────────────────────────────────
server = WorkerOptions(
    entrypoint_fnc=entrypoint,
    agent_name="hotel-assistant",
)
