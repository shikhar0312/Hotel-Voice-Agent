from src.database.connection import database_pool
from src.utils.logger import logger

async def initialize_database():
    logger.info("Initializing database schema...")
    
    async with database_pool.get_connection() as conn:
        create_table_query = """
            CREATE TABLE IF NOT EXISTS call_conversation (
                id SERIAL PRIMARY KEY,
                user_id UUID NOT NULL,
                status VARCHAR(20) DEFAULT 'initiated',
                transcript TEXT,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                duration DOUBLE PRECISION DEFAULT 0,
                stt_audio_duration DOUBLE PRECISION DEFAULT 0,
                tts_characters INTEGER DEFAULT 0,
                stt_cost DOUBLE PRECISION DEFAULT 0,
                tts_cost DOUBLE PRECISION DEFAULT 0,
                llm_cost DOUBLE PRECISION DEFAULT 0,
                total_cost DOUBLE PRECISION DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """
        
        await conn.execute(create_table_query)
        
        logger.info("Database schema initialized successfully")
        logger.info("Created table: call_conversation")

if __name__ == "__main__":
    import asyncio
    
    async def main():
        try:
            await initialize_database()
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Error initializing database: {e}")
            logger.error(f"Database initialization failed: {e}")
    
    asyncio.run(main())
