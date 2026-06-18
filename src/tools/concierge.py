from livekit.agents import function_tool, RunContext
from src.utils.logger import logger

@function_tool
async def fetch_hotel_amenities(context: RunContext):
    """Get information about hotel amenities and services available to guests."""
    logger.info("Fetching hotel amenities")
    
    amenities = """Hotel Amenities:

- 24/7 Front Desk
- Fitness Center (6am-10pm)
- Swimming Pool (7am-9pm)
- Business Center
- Restaurant and Bar (7am-11pm)
- Spa Services (by appointment)
- Free WiFi
- Valet Parking
- Concierge Services
- Room Service (7am-11pm)"""
    
    return amenities

@function_tool
async def fetch_local_recommendations(context: RunContext, category: str):
    """Get local recommendations for restaurants, attractions, shopping, or entertainment."""
    logger.info(f"Getting recommendations for: {category}")
    
    recommendations = {
        'restaurants': """Top Restaurants Nearby:
- The Waterfront Grill (0.5 mi) - Fine dining seafood
- Italian Corner (0.3 mi) - Casual Italian
- Spice and Sizzle (0.8 mi) - Asian fusion
- Local Burger Joint (0.4 mi) - American comfort food""",
        
        'attractions': """Popular Attractions:
- City Museum (1.2 mi) - Art and history
- Downtown Park (0.6 mi) - Scenic trails
- Theater District (1.5 mi) - Live shows
- Waterfront Promenade (0.9 mi) - Shopping and dining""",
        
        'shopping': """Shopping Destinations:
- City Center Mall (1.0 mi) - Major retailers
- Artisan Market (0.7 mi) - Local crafts
- Fashion Avenue (1.3 mi) - Designer boutiques""",
        
        'entertainment': """Entertainment Options:
- Cinema Complex (0.8 mi) - Latest movies
- Comedy Club (1.1 mi) - Live shows nightly
- Jazz Lounge (0.5 mi) - Live music Wed-Sat
- Sports Arena (2.0 mi) - Check event schedule"""
    }
    
    return recommendations.get(category.lower(), "Please specify: restaurants, attractions, shopping, or entertainment")

@function_tool
async def request_housekeeping(context: RunContext, room_number: str, service_type: str):
    """Request housekeeping services for a specific room."""
    logger.info(f"Housekeeping request for room {room_number}: {service_type}")
    
    return f"Housekeeping request submitted for room {room_number}. Service: {service_type}. Estimated time: 30 minutes. Thank you!"
