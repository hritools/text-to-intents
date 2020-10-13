from texttointent                   import TextToIntentSimple
from texttointent.intents.tell      import Joke, Weather, WhatYouCan
from texttointent.slots             import PointInTime

# Create a benchmarking dataset (usually you would like to parse it from .csv)
dataset = [
    ("что с погодой сегодня", Weather.KEYWORD, PointInTime.TODAY),
    ("что завтра с погодой",  Weather.KEYWORD, PointInTime.TOMORROW),
    ("а что ты умеешь делать", WhatYouCan.KEYWORD, None),
    ("никаких ключевых слов тут нет", None, None),
    ("погода обманчива в эти дни", None, None)
]

# Create a parser
tti = TextToIntentSimple(intents=[Joke, Weather, WhatYouCan])

# Obtain a benchmarking report
print(tti.benchmark(dataset))
