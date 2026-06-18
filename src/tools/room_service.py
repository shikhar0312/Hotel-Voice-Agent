from livekit.agents import function_tool, RunContext
from src.utils.logger import logger

@function_tool
async def fetch_room_service_menu(context: RunContext):
    """Get the room service menu with available food and beverage options."""
    logger.info("Fetching room service menu")
    
    menu = """Room Service Menu:
    
Breakfast (7am-11am):
- Continental Breakfast: $18
- Full American Breakfast: $24
- Pancakes: $15

Main Courses (11am-11pm):
- Club Sandwich: $16
- Caesar Salad: $14
- Grilled Chicken: $22
- Steak and Potatoes: $32

Beverages:
- Coffee or Tea: $4
- Soft Drinks: $5
- Wine (glass): $12

All prices include service charge."""
    
    return menu

@function_tool
async def place_room_service_order(context: RunContext, room_number: str, items: str):
    """Place a room service order for a specific room."""
    logger.info(f"Room service order for room {room_number}: {items}")
    
    return f"Room service order placed for room {room_number}. Items: {items}. Estimated delivery: 30-45 minutes. Thank you!"
    