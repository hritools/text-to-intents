from texttointent              import TextToIntentSimple
from texttointent.intents.tell import Joke, Weather, WhatYouCan

# Create a parser
tti = TextToIntentSimple(intents=[Joke, Weather, WhatYouCan])

# Returns an object of either Joke or Weather or WhatYouCan
# In this case, it should be Weather with a slot of type PointInTime
intent = tti.parse("какая завтра будет погода?")
print("{} ({})".format(intent.KEYWORD, intent.concrete_slots[0].value))