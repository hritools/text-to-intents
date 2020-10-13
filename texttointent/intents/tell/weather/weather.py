from ...intent import Intent
from ....slots import PointInTime

class Weather(Intent):
    KEYWORD = "weather"

    @staticmethod
    def help_text():
        return "о погоде"
    
    @staticmethod
    def get_keywords():
        return ["погода", "тепло", "холодно"]

    @staticmethod
    def get_slots():
        return [PointInTime]