from livekit.agents import function_tool, RunContext
from src.utils.guest_data_helper import guest_db
from src.utils.logger import logger

@function_tool
async def lookup_guest_by_room(context: RunContext, room_number: str):
    """Look up guest information by their room number."""
    logger.info(f"Looking up guest in room {room_number}")
    
    guest = await guest_db.find_guest_by_room(room_number)
    
    if guest:
        return f"Guest in room {room_number}: {guest.get('Name', 'Unknown')}. Check-in date: {guest.get('check in date', 'N/A')}. Email: {guest.get('Email', 'N/A')}"
    else:
        return f"No guest found in room {room_number}."

@function_tool
async def lookup_guest_by_name(context: RunContext, name: str):
    """Look up guest information by their name."""
    logger.info(f"Looking up guest by name: {name}")
    
    guest = await guest_db.find_guest_by_name(name)
    
    if guest:
        return f"Found guest {guest.get('Name', 'Unknown')} in room {guest.get('H_room_no', 'N/A')}. Check-in: {guest.get('check in date', 'N/A')}"
    else:
        return f"No guest found with name {name}."
