from ...intent import Intent

class Joke(Intent):
    KEYWORD = "joke"

    @staticmethod
    def get_keywords():
        return ["шутка", "прикол", "анекдот", "анек"]