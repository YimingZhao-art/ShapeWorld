import json
import os

from shapeworld.realizers.realizer import CaptionRealizer
from shapeworld.captions import Attribute, EntityType, Existential, Relation, Selector


class TemplateEnglishRealizer(CaptionRealizer):

    def __init__(self, language):
        if language is None:
            language = 'english'
        super(TemplateEnglishRealizer, self).__init__(language=language)
        self._load_language_spec(language=language)

    def realize(self, captions):
        strings = list()
        for caption in captions:
            if caption is None:
                strings.append('')
                continue
            realized = self._realize_caption(caption=caption)
            strings.append('' if realized is None else realized)
        return strings

    def _realize_caption(self, caption):
        if not isinstance(caption, Existential):
            return None

        relation = caption.body
        if not isinstance(relation, Relation):
            return None

        direction = self._relation_direction(predtype=relation.predtype, value=relation.value)
        if direction is None:
            return None

        subject_type = self._entity_type_from_caption(caption.restrictor)
        reference_type = self._entity_type_from_caption(relation.reference)
        if subject_type is None or reference_type is None:
            return None

        subject = self._entity_phrase(entity_type=subject_type)
        reference = self._entity_phrase(entity_type=reference_type)

        return (
            'there are two shapes {subject} and {reference} . '
            'what is the spatial relationship from the first shape to the second shape ? '
            'the spatial relation is {direction} .'
        ).format(subject=subject, reference=reference, direction=direction)

    def _entity_type_from_caption(self, caption):
        if isinstance(caption, EntityType):
            return caption
        if isinstance(caption, Selector):
            return caption.scope
        return None

    def _relation_direction(self, predtype, value):
        if predtype == 'x-rel':
            return 'left' if value == -1 else 'right'
        if predtype == 'y-rel':
            return 'above' if value == -1 else 'below'
        return None

    def _entity_phrase(self, entity_type):
        attributes = list(entity_type.value)
        words = list()
        for predtype in ('color', 'texture', 'shape'):
            for attribute in attributes:
                if attribute.predtype == predtype:
                    words.append(attribute.value)
        for attribute in attributes:
            if attribute.predtype not in ('color', 'texture', 'shape'):
                words.append(attribute.value)
        if not words:
            return 'a shape'
        article = 'an' if self._starts_with_vowel(word=words[0]) else 'a'
        return '{} {}'.format(article, ' '.join(words))

    def _starts_with_vowel(self, word):
        return word[:1].lower() in ('a', 'e', 'i', 'o', 'u')

    def _load_language_spec(self, language):
        directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dmrs', 'languages')
        language_path = os.path.join(directory, language + '.json')
        if not os.path.isfile(language_path):
            language_path = os.path.join(directory, 'english.json')
        with open(language_path, 'r') as filehandle:
            spec = json.load(filehandle)

        self.attributes = dict()
        for predtype, values in spec.get('attributes', {}).items():
            if predtype in ('relation', 'shapes'):
                continue
            parsed_values = {self._parse_value(value): None for value in values.keys()}
            self.attributes[self._parse_value(predtype)] = parsed_values

        self.relations = dict()
        for predtype, values in spec.get('relations', {}).items():
            parsed_values = {self._parse_value(value): None for value in values.keys()}
            self.relations[self._parse_value(predtype)] = parsed_values

    def _parse_value(self, value):
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                pass
            try:
                return float(value)
            except ValueError:
                pass
        return value
