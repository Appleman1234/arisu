from errbot import BotPlugin, botcmd
import Levenshtein as pylev
class Levenshtein(BotPlugin):
    """Levenshtein plugin for Errbot"""

    @botcmd(split_args_with = ' ')
    def levenshtein(self, msg, args):
        """Calculate levenshtein distance between two words"""
        if len(args) == 2:
            result = "Levenshtein distance: " + str(pylev.distance(args[0],args[1]))
        else:
            result = "Two words are needed to calculate Levenshtein distance"
        return result 
