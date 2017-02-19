# coding=utf8
from errbot import BotPlugin, botcmd

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class Convertor(BotPlugin):
    """Convertor plugin for Errbot"""

    @botcmd(split_args_with = ' ')
    def celcius(self, msg, args):
        """Convert temperature in Fahrenheit to Celcius"""
        result =  "Am I supposed to guess the temperature?..."
        if len(args) == 1 and is_int(args[0]):
            number = int(args[0])
        elif len(args) == 1 and is_float(args[0]):
            number = float(args[0])
        result = "{:.2f}".format((number - 32) * 5.0/9.0) + "\xb0C"
        return result 
    
    @botcmd(split_args_with = ' ')
    def fahrenheit(self, msg, args):
        """Convert temperature in Celcius to Fahrenheit"""
        result =  "Am I supposed to guess the temperature?..."
        if len(args) == 1 and is_int(args[0]):
            number = int(args[0])
        elif len(args) == 1 and is_float(args[0]):
            number = float(args[0])
        result = "{:.2f}".format(9.0/5.0 * number + 32) + "\xb0F"
        return result 
