class Intent:
    def __init__(self, slots=None):
        self.concrete_slots = slots or []

    @staticmethod
    def help_text():
        return ""

    @staticmethod
    def get_keywords():
        """
        Returns a list of keywords associated with this intent.
        """
        return []
        
    @staticmethod
    def get_slots():
        """
        Returns a list of slot types associated with this intent.
        """
        return []