# Text-To-Intents
A library for parsing natural language to a pre-defined set of intents or semantics. The library is meant for flat-structured semantics: intent detection and slot filling with no hierarchies.

## Getting Started

### Installation
```
pip install .
```

### Simple example
```
from texttointent              import TextToIntentSimple
from texttointent.intents.tell import Joke, Weather, WhatYouCan

# Create parser
tti = TextToIntentSimple(intents=[Joke, Weather, WhatYouCan])

# Returns an object of either Joke or Weather or WhatYouCan
# In this case, it should be Weather with a slot of PointInTime type
print(tti.parse("какая завтра будет погода?"))
```

## Intents
Intents are defined using the following information
- A list of **keywords**. Every intent will be matched against their set of keywords.
- A list of **slots**. Types of the slots that should be attached to the intent.

### How to add your own intent?
```
### Define custom intent ###
from texttointent.intents import Intent

class CustomIntent(Intent):
    KEYWORD = "custom"

    @staticmethod
    def get_keywords():
        return ["мой", "набор", "ключевых", "слов"]
    
### Create a parser with your intents of interest ###
from texttointent              import TextToIntentSimple
from texttointens.intents.tell import Joke

tti = TextToIntentSimple(intents=[CustomIntent, Joke])
```
For more examples, check the [intents](intents/) and [slots](slots/) folders.

## Supported Solutions
| Solution | Num Intents per Request | Num Slots per Intent | Numbers Supported
:---:|:---:|:---:|:---:
TextToIntentSimple | 1 | 1 | FALSE |

## Benchmarking
Benchmarking is a crucial part of understanding how good is the system for your particular problem. For this purpose, we provide a simple and convenient interface for benchmarking your datasets against the provided solutions.

### How to benchmark a solution for your dataset?
```
from texttointent              import TextToIntentSimple
from texttointent.intents.tell import Joke, Weather, WhatYouCan
from texttointent.slots        import PointInTime

# Create a benchmarking dataset (usually you would like to parse it from .csv)
# (text, intent type (via an id keyword), slot value)
dataset = [
    ("что с погодой сегодня", Weather.KEYWORD, PointInTime.TODAY),
    ("что завтра с погодой",  Weather.KEYWORD, PointInTime.TOMORROW),
    ("а что ты умеешь делать", WhatYouCan.KEYWORD, None),
    ("никаких ключевых слов тут нет", None, None),
    ("погода обманчива в эти дни", None, None)
]

# Create a parser
tti = TextToIntentSimple(intents=[Joke, Weather, WhatYouCan])

# Obtain a benchmarking report (sci-kit classiciation report)
print(tti.benchmark(dataset))
```

## Fine-tuning
Some solutions are trainable. If you want to fit your particular dataset, just call ```fit```.

```
from texttointent              import TextToIntentSimple
from texttointent.intents.tell import Joke, Weather, WhatYouCan
from texttointent.slots        import PointInTime

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

# Fit simple solution for your dataset
# (No gain for this particular dataset is expected)
fit_report = tti.fit(dataset)
print(fit_report)
```

