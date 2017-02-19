from errbot import BotPlugin, botcmd
from bs4 import BeautifulSoup
import requests

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class NumberSpell(BotPlugin):
    """NumberSpell plugin for Errbot"""


    def get_number_kanji(self,number):
        url = "http://www.sljfaq.org/cgi/numbers.cgi?number=%s&usedaiji=0" % number
        response = requests.get(url)
        soup = BeautifulSoup(response.content,"lxml")
        results = soup.find_all("td")
        kanji = str(results[3].string)
        if number[0] == "-":
            kanji = u"\u30de\u30a4\u30ca\u30b9" + kanji[2:]
        kana = str(results[4].string)
        resultstring = kanji.strip("\n") + " (" + kana.strip("\n")+ ")"
        return resultstring

    
    def get_spelling_for_number(self,number):
        if is_int(number):
            if 'cache' not in self:
                self['cache'] = dict()

            if number in self['cache']:
                result = self['cache'][number]
            else:
                 number_kanji = self.get_number_kanji(str(number))
                 d = self['cache']
                 d[number] = number_kanji
                 self['cache'] = d
                 result = number_kanji
        else:
            result = "That isn't a number"
        return result

    @botcmd(split_args_with = ' ')
    def ns(self, msg, args):
        """Print spelling for the number"""
        result = 'Am I supposed to guess the number?...'
        if args:
            number = args[0]
            result = self.get_spelling_for_number(number)
        return result 
