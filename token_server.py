from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from livekit import api
from src.config.settings import settings
import uuid
import os
import logging

public_url = os.getenv("PUBLIC_LIVEKIT_URL", "ws://localhost:7880")
agent_name = os.getenv("LIVEKIT_AGENT_NAME", "hotel-assistant")
logger = logging.getLogger("token_server")

app = FastAPI(title="LiveKit Token API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TokenRequest(BaseModel):
    identity: str = None
    room_name: str = "test-room"

class TokenResponse(BaseModel):
    token: str
    url: str
    identity: str
    room: str

@app.get("/api/token")
async def generate_token_get(identity: str = None, room: str = "test-room"):
    return await create_token(identity, room)

@app.post("/api/token")
async def generate_token_post(request: TokenRequest):
    return await create_token(request.identity, request.room_name)


async def ensure_agent_dispatch(room_name: str):
    async with api.LiveKitAPI(
        url=settings.LIVEKIT_URL,
        api_key=settings.LIVEKIT_API_KEY,
        api_secret=settings.LIVEKIT_API_SECRET,
    ) as lkapi:
        # In some local/self-hosted setups, listing dispatches can fail before
        # a room has an assigned node. Continue and still try create_dispatch.
        try:
            dispatches = await lkapi.agent_dispatch.list_dispatch(room_name)
            for d in dispatches:
                await lkapi.agent_dispatch.delete_dispatch(d.id, room_name)
        except Exception as list_error:
            logger.warning("Could not list existing dispatches for room %s: %s", room_name, list_error)

        await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                room=room_name,
                agent_name=agent_name,
                metadata="auto-dispatched-by-token-server",
            )
        )

async def create_token(identity: str = None, room_name: str = "test-room"):
    if not identity:
        identity = f"user-{uuid.uuid4().hex[:8]}"
    
    try:
        token = api.AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET
        )
        token.with_identity(identity)
        token.with_name(identity)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
        ))
        
        jwt_token = token.to_jwt()
        # Agent dispatch is best-effort: token issuance should not fail when
        # dispatch API is temporarily unavailable.
        try:
            await ensure_agent_dispatch(room_name)
        except Exception as dispatch_error:
            logger.warning("Agent dispatch skipped for room %s: %s", room_name, dispatch_error)
        
        return TokenResponse(
    token=jwt_token,
    url=public_url,
    identity=identity,
    room=room_name
)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
