import pymorphy2
import editdistance
import numpy as np
import string
import nltk
import sys

from sklearn.metrics import classification_report
from collections     import OrderedDict
from tqdm            import tqdm
from itertools       import product
from typing          import List, Tuple

# Make forms match as well
# Verb - verb: OK
# Verb - noun: WRONG
# Noun - noun: OK
# Verb - adjective: WRONG
# Noun - adjective: WRONG

class TextToIntentSimple:
    def __init__(self, intents, intent_max_distance=3, slot_max_distance=19, max_window_size=3):
        self._morph               = pymorphy2.MorphAnalyzer()
        self._intent_max_distance = intent_max_distance
        self._slot_max_distance   = slot_max_distance
        self._intents             = intents
        self._max_window_size     = max_window_size # Yet to be used

    def fit(self, dataset):
        """
        Returns:
            best metric (float), best sklearn classification report (dict)
        """
        def target_metric(report):
            return report["weighted avg"]["f1-score"]

        # Find best distance for unknown intent
        best_metric         = 0.0
        best_report         = None

        best_params         = (self._intent_max_distance, self._slot_max_distance, self._max_window_size)
        start               = 3
        num_steps           = 17
        parameters          = product(range(start, start + num_steps), range(start, start + num_steps), range(1, 4))
        for intent_max_dist, slot_max_dist, max_window_size in tqdm(parameters, total=num_steps**2 * 3):
            # Substitue parameters
            self._intent_max_distance = intent_max_dist
            self._slot_max_distance   = slot_max_dist
            self._max_window_size     = max_window_size

            cur_report          = self.benchmark(dataset, output_dict=True)
            cur_metric          = target_metric(cur_report)
            if cur_metric >= best_metric:
                best_report = cur_report
                best_metric = cur_metric
                best_params = (intent_max_dist, slot_max_dist, max_window_size)

        # Set the best found model
        self._intent_max_distance = best_params[0]
        self._slot_max_distance   = best_params[1]
        self._max_window_size     = best_params[2]
        
        return best_metric, best_report

    def benchmark(self, dataset, output_dict=False):
        """
        It is recommended to obtain score for the semantic parser on your particular dataset.
        (text, intent_keyword, slot_value)
        Supports only one intent with one slot.

        Returns:
            sklearn classification report (either a dictionary or a string, defaults to string)
        """
        # TODO: Make it more explicit (this behaviour is not clear without looking here)
        # TODO: Merge intents found in dataset and the passed intents
        def get_label(intent_keyword, slot_value):
            if intent_keyword is None:
                return "unknown_empty"
            if slot_value is None:
                slot_value = ""
            else:
                slot_value = "_" + slot_value
            return "{}{}".format(intent_keyword, slot_value)
        def get_label_object(intent):
            # If there was no intent, default to this
            if intent is None:
                return get_label("unknown", "empty")

            if len(intent.get_slots()) == 0:
                return get_label(intent.KEYWORD, None)
            else:
                if len(intent.concrete_slots) == 0:
                    slot_value = "empty"
                else:
                    slot_value = intent.concrete_slots[0].value

                    # If could not determine the slot, it's unknown
                    if slot_value == None:
                        slot_value = "unknown"

                return get_label(intent.KEYWORD, slot_value)

        ### Parse all presented intents and keywords
        found_intents = OrderedDict()
        for record in dataset:
            target_text           = record[0]
            target_intent_keyword = record[1]
            target_slot_value     = record[2]
            target_name           = get_label(target_intent_keyword, target_slot_value)
            if target_name not in found_intents:
                found_intents[target_name] = len(found_intents)

        ### Make predictions
        y_true, y_pred = [], []
        for record in dataset:
            target_text           = record[0]
            target_intent_keyword = record[1]
            target_slot_value     = record[2]
            target_name           = get_label(target_intent_keyword, target_slot_value)

            # Predict an intent
            pred_intent = self.parse(target_text)
            pred_name   = get_label_object(pred_intent)

            if pred_name not in found_intents:
                found_intents[pred_name] = len(found_intents)

            y_true.append(found_intents[target_name])
            y_pred.append(found_intents[pred_name])

        return classification_report(y_true, y_pred, target_names=list(found_intents.keys()), output_dict=output_dict)

    def parse(self, text, intents=None):
        # Use default intents if not provided
        if intents is None:
            intents = self._intents

        # Parse intent
        intent = self._get_most_similar_entity(text, 
            intents, 
            keywords=[intent.get_keywords() for intent in intents],
            unknown_dist=self._intent_max_distance,
            unknown=None)
        
        # Could not identify the intent
        if intent is None:
            return None
            
        # Parse slot (No support for intents with more than one slot)
        slot = self.parse_slot(text, intent)

        return intent([slot])

    def parse_slot(self, text: str, intent):
        """
        Parsing the target text for a slot conditioned on the passed intent.
        """
        # Parse slot (No support for intents with more than one slot)
        if len(intent.get_slots()) == 1:
            slot_type   = intent.get_slots()[0]
            slot_values = slot_type.get_values()
            slot = self._get_most_similar_entity(text, 
                slot_values, 
                keywords=[slot_type.get_keywords_by_value(value) for value in slot_values],
                unknown_dist=self._slot_max_distance,
                unknown=None)
            return slot_type(slot)
        else:
            return None

    def _get_most_similar_entity(self, text, entities, keywords, unknown_dist, unknown):
        """
        Every entity is paired with its list of keywords.
        entities = [...]
        keywords = [[], [], ...]
        """
        min_dist   = sys.maxsize
        min_entity = None
        for keywords, entity in zip(keywords, entities):
            # Skip empty entities
            if len(keywords) == 0:
                continue

            # Find minimum distance between the passed text and the current keyword (or keyphrase)
            entity_distance = min([self._min_distance_between_texts(text, keyword) for keyword in keywords])
            if entity_distance < min_dist:
                min_entity = entity
                min_dist = entity_distance

        if min_dist < unknown_dist:
            return min_entity
        else:
            return unknown

    def _text_to_normal_forms(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Substitutes words with their normal forms.

        Returns:
            List[normal_forms], List[part of speech]
        """
        words        = nltk.word_tokenize(text)
        words        = [self._morph.parse(word)[0] for word in words]
        normal_forms = [word.normal_form for word in words]
        tags         = [word.tag.POS for word in words]

        return normal_forms, tags

    def _min_distance_between_texts(self, src: str, target: str) -> int:
        src_norms, _     = self._text_to_normal_forms(src)
        tar_norms, _     = self._text_to_normal_forms(target)
        target_text      = " ".join(tar_norms)
        cur_min_distance = sys.maxsize

        # Linear time (of normal forms)
        for ind, word in enumerate(src_norms):
            cur_text = word
            cur_min_distance = min(editdistance.distance(cur_text, target_text), cur_min_distance)
            for word1 in src_norms[ind+1:ind+1+self._max_window_size]:
                cur_text = cur_text + " " + word1
                cur_min_distance = min(editdistance.distance(cur_text, target_text), cur_min_distance)

        return cur_min_distance

            