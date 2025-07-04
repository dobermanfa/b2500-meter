import logging
import tibber
from .base import Powermeter

logger = logging.getLogger(__name__)

class TibberPowermeter(Powermeter):
    def __init__(self, config):
        self.access_token = config.get("ACCESS_TOKEN")
        self.home_id = config.get("HOME_ID")
        self.user_agent = "home-assistant/b2500-meter"
        self.account = tibber.Account(self.access_token)
        self.home = next((h for h in self.account.homes if h.id == self.home_id), None)
        if not self.home:
            raise ValueError(f"Home with ID {self.home_id} not found in Tibber account.")
        
        self.power_consumption = 0.0
        self.power_production = 0.0
        
        # Store reference to handler to avoid garbage collection
        def _update_power_data(data: tibber.LiveMeasurement):
            logger.debug(f"Received live measurement data: {data.power}, production: {data.power_production}")
            self.power_consumption = getattr(data, 'power', 0.0)
            self.power_production = getattr(data, 'power_production', 0.0)
        self._update_power_data = _update_power_data
        self.home.event("live_measurement")(_update_power_data)
        
        try:
            self.home.start_live_feed(user_agent=self.user_agent)
        except Exception as e:
            logger.error(f"Failed to start Tibber live feed: {e}")

    def get_powermeter_watts(self):
        logger.debug(f"Calculating power: consumption={self.power_consumption}, production={self.power_production}")
        return [self.power_consumption - self.power_production]

    def wait_for_message(self, timeout=5):
        """WebSocket connection is already maintained by Tibber library"""
        pass
