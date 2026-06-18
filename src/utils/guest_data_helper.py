import pandas as pd
import aiofiles
import asyncio
import os
from typing import Optional, Dict, List
from src.utils.logger import logger

class GuestDatabase:
    
    def __init__(self, excel_path: str = "data/guests.xlsx"):
        self.excel_path = excel_path
        self.guests: List[Dict] = []
        self._loaded = False
    
    async def load_guests(self):
        if self._loaded:
            return
            
        try:
            if not os.path.exists(self.excel_path):
                logger.warning(f"Guest data file not found: {self.excel_path}")
                self.guests = []
                self._loaded = True
                return
            
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(None, pd.read_excel, self.excel_path)
            self.guests = df.to_dict('records')
            self._loaded = True
            logger.info(f"Loaded {len(self.guests)} guests from database")
        except Exception as e:
            logger.error(f"Error loading guest data: {e}")
            self.guests = []
            self._loaded = True
    
    async def ensure_loaded(self):
        if not self._loaded:
            await self.load_guests()
    
    async def find_guest_by_room(self, room_number: str) -> Optional[Dict]:
        await self.ensure_loaded()
        
        for guest in self.guests:
            if str(guest.get('H_room_no', '')) == str(room_number):
                return guest
        return None
    
    async def find_guest_by_name(self, name: str) -> Optional[Dict]:
        await self.ensure_loaded()
        
        name_lower = name.lower()
        for guest in self.guests:
            if name_lower in str(guest.get('Name', '')).lower():
                return guest
        return None
    
    async def find_all_guests(self) -> List[Dict]:
        await self.ensure_loaded()
        return self.guests

guest_db = GuestDatabase()
