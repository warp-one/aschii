from random import randint

import libtcodpy as libtcod

# colors = {"base":libtcod.grey, "keyword":libtcod.red}

basic_red = {"base":libtcod.grey, "keyword":libtcod.dark_red, "letters":libtcod.red}
basic_grey = {"base":libtcod.grey, "keyword":libtcod.grey, "letters":libtcod.white}
basic_white = {"base":libtcod.grey, "keyword":libtcod.light_grey, "letters":libtcod.white}
basic_green = {"base":libtcod.grey, "keyword":libtcod.dark_green, "letters":libtcod.green}


def make_color_scheme(**kwargs):
    colors = {"base":libtcod.grey, "keyword":libtcod.red}
    for c in kwargs:
        colors[c] = kwargs[c]
    return colors


class ColorScheme(object):
    def __init__(self, colors=None):
        self.colors = colors
        
    def get_colors(self, phrase, sentence, in_range, len_guesses):
        letter_colors = [self.colors["base"] for l in sentence]
        if in_range:
            phrase_index = sentence.find(phrase)
            phrase_end = phrase_index + len(phrase)
            guess_index = phrase_index + len_guesses
            len_unguessed = len(phrase) - len_guesses
            letter_colors[phrase_index:guess_index] = [self.colors["letters"]] * len_guesses
            letter_colors[guess_index:phrase_end] = [self.colors["keyword"]] * len_unguessed
        return letter_colors
        
      
class SparklyKeyword(ColorScheme):
    def get_colors(self, phrase, sentence, in_range, _):
        letter_colors = [self.colors["base"] for l in sentence]
        if in_range:
            phrase_index = sentence.find(phrase)
            phrase_end = phrase_index + len(phrase)
            keyword_color = [self.colors["keyword"]] * len(phrase)
            for i, kc in enumerate(keyword_color):
                if not randint(0, 7):
                    kc += libtcod.grey
                    keyword_color[i] = kc
            letter_colors[phrase_index:phrase_end] = keyword_color
        return letter_colors
    