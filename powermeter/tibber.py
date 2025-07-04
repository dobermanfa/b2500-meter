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
        
        self.power_consumption = 0
        self.power_production = 0
               
        @self.home.event("live_measurement")
        def update_power_data(data):
            self.power_consumption = data.power
            self.power_production = data.power_production or 0
            
        self.home.start_live_feed(user_agent=self.user_agent)

    def get_powermeter_watts(self):
        return int(self.power_consumption - self.power_production)

    def wait_for_message(self, timeout=5):
        """WebSocket connection is already maintained by Tibber library"""
        pass
