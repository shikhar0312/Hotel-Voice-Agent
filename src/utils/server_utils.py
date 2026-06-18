import time
import uuid
from livekit.agents import JobContext, JobProcess, metrics
from src.config.settings import settings
from src.infrastructure.vad import VADFactory
from src.utils.logger import create_logger
from src.utils.cost_calculator import calculate_call_costs
from src.utils.call_data import persist_call_record, create_call_record
from src.utils.usage_extractor import extract_usage_metrics
from src.utils.transcript_builder import build_transcript

server_logger = create_logger("server_utils", settings.LOG_LEVEL)

class ServerUtils:
    @staticmethod
    def initialize_vad(proc: JobProcess) -> None:
        server_logger.info("Prewarming - loading VAD model via factory...")
        proc.userdata["vad"] = VADFactory.get_loaded_vad(settings)
        server_logger.info("VAD model loaded successfully")

    @staticmethod
    async def handle_session_end(ctx: JobContext) -> None:
        try:
            call_data = ctx.proc.userdata.get("call_data", {})

            duration = time.time() - call_data.get("start_time", time.time())
            transcript = build_transcript(call_data.get("session"))

            metrics_data = extract_usage_metrics(call_data.get("usage_collector"))
            costs = calculate_call_costs(
                metrics_data["input_tokens"],
                metrics_data["output_tokens"],
                metrics_data["stt_audio_duration"],
                metrics_data["tts_characters"]
            )

            conversation = create_call_record(call_data, duration, transcript, costs)
            result = await persist_call_record(conversation)

            if result:
                server_logger.info(f"💾 Call saved to DB - ID: {result}")

            server_logger.info(f"📞 Call ended - Duration: {duration:.2f}s, Cost: ${costs['total_cost']:.4f}")

        except Exception as e:
            server_logger.error(f"Error in handle_session_end: {e}")

    @staticmethod
    def initialize_call_data(ctx: JobContext, session, usage_collector: metrics.UsageCollector) -> None:
        ctx.proc.userdata["call_data"] = {
            "start_time": time.time(),
            "user_id": uuid.uuid4(),
            "usage_collector": usage_collector,
            "session": session,
        }
