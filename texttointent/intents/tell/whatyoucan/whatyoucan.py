from ...intent import Intent

class WhatYouCan(Intent):
    KEYWORD = "whatyoucan"

    @staticmethod
    def get_keywords():
        return ["умеешь", "функционал", "функции"]