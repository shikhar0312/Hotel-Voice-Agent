from livekit.agents import function_tool, RunContext
from src.utils.logger import logger

@function_tool
async def end_call(context: RunContext):
    """End the current call session when the guest says goodbye or indicates they are done."""
    logger.info("Guest ended the call - initiating graceful shutdown")
    
    context.session.shutdown(drain=True)
    return "Call ended successfully. Goodbye!"
