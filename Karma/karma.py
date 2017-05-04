from errbot.backends.irc import IRCRoom
from errbot import BotPlugin, botcmd,  re_botcmd
from bs4 import BeautifulSoup
from itertools import chain
import requests
import string
import random
import re
import json

japanese_regex = re.compile(r'[\u3040-\u30FF\u4E00-\u9FC2\uFF61-\uFF9D\u31F0-\u31FF\u3000-\u303F]',re.UNICODE)
command_regex = re.compile('^\!\w')
CONFIG_TEMPLATE = {'byself': False,'feedback' : True, 'numberspell': False }


class Karma(BotPlugin):
    """Karma plugin for Errbot"""

    def configure(self, configuration):
        if configuration is not None and configuration != {}:
            config = dict(chain(CONFIG_TEMPLATE.items(),
                configuration.items()))
        else:
            config = CONFIG_TEMPLATE
        super(Karma, self).configure(config)

    def get_configuration_template(self):
        return CONFIG_TEMPLATE 
    
    def _update_value_type(self,who,value_type,amount,method='+'):
        """Update value_type for specific user.

        :who: nickname of IRC user
        :value_type: value_type
        :amount: amount
        :method: '+' or '-'

        """
        value = self.get_value_type(who,value_type)
        value = int(value) 
        try:
            if method == '+':
                d = self[value_type]
                d[who] = value + amount
                self[value_type] = d 
            else:
                d = self[value_type]
                d[who] = value - amount
                self[value_type] = d 
        except Exception as e:
            self.log.debug("update %s fail, e: %s" % (value_type,e), DEBUG_LEVEL)

    def promote_value_type(self, who,value_type,amount):
        """Promote valuetype for specific user.

        :who: nickname of IRC user
        :value_type: value_type
        :amount: amount

        """
        return self._update_value_type(who,value_type,amount, '+')

    def demote_value_type(self, who,value_type,amount):
        """Demote valuetype for specific user.

        :who: nickname of IRC user
        :value_type: value_type
        :amount: amount

        """
        return self._update_value_type(who,value_type,amount, '-')

    def _parse_msg(self,msg, amount,method='+'):
        """Parse the message.

        :msg: message
        :returns: who, method,amount

        """
        try:
            who = msg.body.split(method)[0].strip().split().pop()
            who = who.rstrip('のがは紳士変態へんたいロリコンではじゃな無いあ有りません')
        except Exception as e:
            self.log.debug("parse message fail - %s." % (e))
            return None
        return who, method, amount

    def parse_promote(self,msg):
        """Parse the message with '++'.

        :msg: message
        :returns: who,method,amount

        """
        return self._parse_msg(msg,1, method='+')

    def parse_hentai_promote(self,msg):
        """Parse the message

        :msg: message
        :returns: who,method,amount

        """
        return self._parse_msg(msg, 5,method='+')
    def parse_demote(self,msg):
        """Parse the message with '--'.

        :msg: message
        :returns: who,method,amount

        """
        return self._parse_msg(msg,1, method='-')

    def parse_hentai_demote(self,msg):
        """Parse the message

        :msg: message
        :returns: who,method,amount

        """
        return self._parse_msg(msg,3, method='-')

    def get_reply_message(self,value_type,sender,who,value,delta):
        """ Get message to reply to value change
        :value_type
        :sender
        :who
        :value
        :delta
        """
        reply_message = ""
        choices = []
        if value_type == 'karma':
            if delta > 0:
                choices = ["#{receiver}++!" ,"#{receiver}, #{sender} likes you.", "#{receiver}, point for you."]
            else:
                choices = ["#{receiver}--!" ,"#{receiver}, #{sender}  dislikes you.", "#{receiver}, point from you."]
            choice = random.choice(choices)
            choice = choice.replace("#{receiver}",who)
            choice = choice.replace("#{sender}",sender)
            choice = choice.replace("#{receiver_points}",str(value))
            reply_message = choice 
        elif value_type == 'hentai':
            if delta == -3:
                choices = ["#{receiver} became more of a gentleman!","#{sender} has stolen #{receiver}'s porn collection!","Let it be known, that #{receiver}'s hentai power has dropped to lvl #{receiver_points}."]
            elif delta == 1:
                choices = ["#{receiver} has become even more perverted than ever!","#{sender} can't resist #{receiver}'s ero-charm!", "Let it be known, that #{receiver} is pervert #{receiver_points}lvl."]
            elif delta == 5:
                choices = ["#{receiver} has trespassed the society morals!","#{sender} wishes to be #{receiver}'s little girlfriend!", "Let it be known, that #{receiver} prefers girls #{receiver_points} years younger than self."]
            choice = random.choice(choices)
            choice = choice.replace("#{receiver}",who)
            choice = choice.replace("#{sender}",sender)
            choice = choice.replace("#{receiver_points}",str(value))
            reply_message = choice 
        else:
            reply_message = "%s's new %s: %s " % (who, value_type, value)
        return reply_message
    
    def get_value_type(self,who,value_type):
        value = str(0)
        if value_type in self:
            if who in self[value_type]:
                value = self[value_type][who]
            else:
                self[value_type][who] = value 
            
        else:
            self[value_type] = { who : value } 
        return value

    def get_value_for_status_type(self,msg,args,value_type):
        result = ""
        if len(args) == 1:
            if len(args[0]) == 0:
                who = msg.frm.nick
            else:
                who = args[0]
            value = self.get_value_type(who,value_type)
            if value == "0" or value is None:
                if value_type == "karma":
                    result = "%s has no karma." % who
                elif value_type == "language":
                    result = "%s has no language points." % who
                elif value_type == "hentai":
                    result = "%s doesn't seem to be a pervert." % who
            else:
                pm = self._bot.plugin_manager
                if self.config['numberspell']:
                    numberspell = pm.get_plugin_obj_by_name('NumberSpell')
                    result = "%s's %s points are : %s" % (who, value_type,numberspell.get_spelling_for_number(value))
                else:
                    result = "%s's %s points are : %s" % (who, value_type,value)
        else:
            if value_type == "karma":
                command = "karma"
            elif value_type == "language":
                command = "lp"
            elif value_type == "hentai":
                command = "hp"
            result = ("!%s <nick> - Reports %s status for <nick>." % (command, value_type) )
        return result

    def update_value_for_status_type(self,msg,  value_type, parse_fun, value_type_fun):
        """Update value_type status for specific user"""
        who,method,amount = parse_fun(msg)
        # Language points come from the speaker and not the message
        if value_type == "language":
            who = msg.frm.nick 
        if who:
            #. not allow self (pro|de)mote
            if not self.config['byself'] and value_type != "language":
                if who == msg.frm.nick:
                    return
            #. update value_type
            previous_value =  self.get_value_type(who,value_type)
            value_type_fun(who,value_type,amount)
            value =  self.get_value_type(who,value_type)
            delta = int(value) - int(previous_value)
            if self.config['feedback'] and value_type != "language":
                reply_message = self.get_reply_message(value_type,msg.frm.nick,who,value,delta)
                return reply_message
    
    def callback_message(self, mess):
        is_a_command = command_regex.match(mess.body)
        
        if "#" in str(mess.to) and is_a_command is None:
            match = japanese_regex.match(mess.body)
            if match:
                self.update_value_for_status_type(mess,'language', self.parse_promote, self.promote_value_type)
            else:
                self.update_value_for_status_type(mess,'language', self.parse_demote, self.demote_value_type)

    @re_botcmd(pattern=r'^[[\w][\S]+[がは]?(紳士|(変態|へんたい|ロリコン)(では|じゃ)?([な無]い|[あ有]りません))',prefixed=False)
    def demote_hentai(self, msg, args):
        """Command to lower the hentai point status for specific user""" 
        return self.update_value_for_status_type(msg,'hentai', self.parse_hentai_demote, self.demote_value_type)

    @re_botcmd(pattern=r'^[[\w][\S]+の?(変態|へんたい)$',prefixed=False)
    def promote_hentai(self, msg, args):
        """Command to raise the hentai point status for specific user""" 
        return self.update_value_for_status_type(msg,'hentai', self.parse_hentai_promote, self.promote_value_type)

    @re_botcmd(pattern=r'^[[\w][\S]+の?ロリコン$',prefixed=False)
    def promote_hentai_large(self, msg, args):
        """Command to raise the hentai point status for specific user significantly"""
        return self.update_value_for_status_type(msg,'hentai', self.parse_hentai_promote, self.promote_value_type)

    @re_botcmd(pattern=r'^[[\w][\S]+[\+]{2}',prefixed=False)
    def promote_karma(self,msg, args):
        """Update karma status for specific user if get '++' message."""
        return self.update_value_for_status_type(msg,'karma', self.parse_promote, self.promote_value_type)

    @re_botcmd(pattern=r'^[[\w][\S]+[\-]{2}',prefixed=False)
    def demote_karma(self,msg, args):
        """Update karma status for specific user if get '--' message."""
        return self.update_value_for_status_type(msg,'karma', self.parse_demote, self.demote_value_type)


    @botcmd(split_args_with = ' ')
    def karma(self, msg, args):
        """Command to show the karma status for specific user"""
        result = self.get_value_for_status_type(msg,args,'karma')
        return result

    @botcmd(split_args_with = ' ')
    def hp(self, msg, args):
        """Command to show the hentai point status for specific user""" 
        result = self.get_value_for_status_type(msg,args,'hentai')
        return result 

    @botcmd(split_args_with = ' ')
    def lp(self, msg, args):
        """Command to show the language point status for specific user""" 
        result = self.get_value_for_status_type(msg,args,'language')
        return result 

