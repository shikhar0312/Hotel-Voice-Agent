import logging

def create_logger(name: str = "hotel_agent", log_level: str = "INFO"):
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.propagate = False
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def suppress_livekit_debug_logs():
    livekit_logger = logging.getLogger("livekit.agents")
    livekit_logger.setLevel(logging.INFO)
    
    for noisy_logger in ["livekit", "livekit.plugins", "httpx", "httpcore", "asyncio"]:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)

logger = create_logger()
suppress_livekit_debug_logs()
