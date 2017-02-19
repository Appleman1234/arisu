from errbot import BotPlugin, botcmd
import romkan
import kroman

class Language(BotPlugin):
    """Language plugin for Errbot"""


    @botcmd(split_args_with = ' ')
    def kana(self, msg, args):
        """Converts Romazi to kana"""
        result =  "Am I supposed to guess the word you want?..."
        word = None
        if len(args) == 1: 
            word = args[0]
        elif len(args) > 1: 
            word = " ".join(args)
        if word is not None:
            if word.isupper():
                result = romkan.to_katakana(word)
            elif word.islower():
                result = romkan.to_hiragana(word)
        return result 

    @botcmd(split_args_with = ' ')
    def romaja(self, msg, args):
        """Converts given hangul to romaja"""
        result =  "Am I supposed to guess the word you want?..."
        word = None
        if len(args) == 1: 
            word = args[0]
        elif len(args) > 1: 
            word = " ".join(args)
        if word is not None:
            result = kroman.parse(word)
        return result 
