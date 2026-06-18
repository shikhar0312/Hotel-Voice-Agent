# Hotel Voice Agent

A production-ready LiveKit voice agent for hotel guest services, designed to handle inbound SIP calls and web-based audio. The agent relies on Google Gemini for intelligent reasoning and Deepgram for real-time speech-to-text (STT) and text-to-speech (TTS).

## Features

- **Guest Lookup**: Search guest information by room number or name
- **Room Service**: Browse menu and place orders
- **Concierge Services**: Hotel amenities, local recommendations, housekeeping requests
- **Voice-First Design**: Optimized for natural phone conversations
- **Clean Architecture**: Centralized configuration, modular design

## Prerequisites

- Docker & Docker Compose
- Google Gemini API Key
- Deepgram API Key

## Quick Start

### 1. Clone & Setup

```bash
git clone <repository-url>
cd Livekit-Agent
```

### 2. Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# LiveKit Configuration (Required)
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret1234567890secret1234567890

# Google Gemini Configuration (Required)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Deepgram Configuration (Required)
DEEPGRAM_API_KEY=your_deepgram_api_key_here
DEEPGRAM_STT_MODEL=nova-2
DEEPGRAM_TTS_MODEL=aura-asteria-en

# Hotel Configuration (Optional)
HOTEL_NAME=Grandview Hotel
ASSISTANT_NAME=Kelly
LOG_LEVEL=INFO

# Database Configuration
DB_HOST=db
DB_PORT=5432
DB_NAME=hotel_room_service
DB_USER=postgres
DB_PASSWORD=Admin
```

> **⚠️ Important**: Never commit real API keys to version control.

### 3. Start the Project (Docker)

This project runs fully within Docker. From the project root, start all services:

```bash
docker-compose up -d
```

This starts:
- **Redis** on localhost:6379 (LiveKit dependency)
- **Postgres DB** on localhost:5432 (Guest and Call data)
- **LiveKit Server** on ws://localhost:7880
- **Token Server** on localhost:8080
- **Agent Server** on localhost:8081
- **Frontend UI** on localhost:8501

To verify services are running:

```bash
docker ps
```

To follow the agent's logs:
```bash
docker logs livekit-agent -f
```

## Testing the Agent

### Web Browser Testing

1. **Open the Test Client**:
   - Open [http://localhost:8501](http://localhost:8501) in your browser (Streamlit Frontend UI)
   - Alternatively, you can use the token server to generate tokens directly if building a custom UI.
2. Click "Connect & Test Agent"
3. Start speaking!

## Test Scenarios

### Guest Lookup
- "What's the guest name in room 101?"
- "Look up John Doe"

### Room Service
- "Show me the room service menu"
- "Order a club sandwich for room 101"

### Hotel Information
- "What amenities does the hotel have?"
- "I need housekeeping"

### Local Recommendations
- "Recommend restaurants nearby"
- "What attractions are nearby?"

## Project Structure

```
Livekit-Agent/
├── src/
│   ├── config/          # Centralized settings
│   ├── agent/           # Agent logic (hotel_assistant_agent.py)
│   ├── tools/           # Function tools (guest lookup, room service, concierge)
│   ├── models/          # Data models
│   ├── utils/           # Logging utilities
├── docker-compose.yml   # Docker compose configuration
├── livekit.yaml         # LiveKit server config
├── Dockerfile           # Backend container build instructions
├── Dockerfile.ui        # Frontend container build instructions
├── agent_server.py      # Main agent server entrypoint
├── token_server.py      # Token generation API
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (create this)
```

## Local Development (Optional)

Although the project runs in Docker, you may want to set up a local virtual environment for your IDE (like VS Code) to get autocompletion and linting:

```bash
# Create a virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```
> **Note:** The `.venv` folder is specific to your operating system and absolute paths. It is added to your `.gitignore` and **should not** be shared with your team or committed to version control.

## Troubleshooting

### Agent not responding
- Check agent logs for errors: `docker logs livekit-agent`
- Verify Gemini and Deepgram API keys are valid in your `.env`

### No audio in browser
- Check microphone permissions in the browser
- Verify LiveKit server is accessible
- Check browser console for WebRTC errors

### Docker issues
```bash
# Restart services completely
docker-compose down -v
docker-compose up -d --build
```

# Hotel-Voice-Agent
