import logging
import tibber
from .base import Powermeter
from .throttling import Throttling

logger = logging.getLogger(__name__)

class TibberPowermeter(Powermeter):
    def __init__(self, config):
        self.access_token = config.get("ACCESS_TOKEN")
        self.home_id = config.get("HOME_ID")
        self.throttle = Throttling(config.get("THROTTLE_INTERVAL", 2))
        self.user_agent = "home-assistant/b2500-meter"
        self.account = tibber.Account(self.access_token)
        self.home = None
        self.power_consumption = 0
        self.power_production = 0
        
        # Setup synchronous wrapper around async Tibber API
        self.home = self.account.get_home(self.home_id)
        
        @self.home.event("live_measurement")
        def update_power_data(data):
            self.power_consumption = data.power
            self.power_production = data.power_production or 0
            
        self.home.start_live_feed(user_agent=self.user_agent)

    def get_powermeter_watts(self):
        self.throttle.wait()
        return int(self.power_consumption - self.power_production)

    def wait_for_message(self, timeout=5):
        """WebSocket connection is already maintained by Tibber library"""
        pass
