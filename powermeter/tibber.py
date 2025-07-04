import logging
import asyncio
import tibber
from .base import Powermeter
from .throttling import Throttling

logger = logging.getLogger(__name__)

class TibberPowermeter(Powermeter):
    def __init__(self, config):
        self.access_token = config.get("ACCESS_TOKEN")
        self.throttle = Throttling(config.get("THROTTLE_INTERVAL", 2))
        self.tibber_connection = tibber.Tibber(self.access_token)
        self.loop = asyncio.new_event_loop()
        self.power_consumption = 0
        self.power_production = 0
        
        async def setup_connection():
            await self.tibber_connection.update_info()
            home = self.tibber_connection.get_homes()[0]
            await home.rt_subscribe(lambda data: self._callback(data))
            
        self.loop.run_until_complete(setup_connection())

    def _callback(self, data):
        # Store both consumption and production values with fallback to 0
        self.power_consumption = data.get("power", 0)
        self.power_production = data.get("powerProduction", 0)

    def get_powermeter_watts(self):
        self.throttle.wait()
        return int(self.power_consumption - self.power_production)

    def wait_for_message(self, timeout=5):
        """WebSocket connection is already maintained by Tibber library"""
        pass
