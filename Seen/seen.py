from errbot.backends.irc import IRCRoom
from errbot import BotPlugin, botcmd,  re_botcmd
from itertools import chain
import datetime
import math
import dateutil.relativedelta

class Seen(BotPlugin):
    """Seen plugin for Errbot"""

    def human_readable_offset(self,time1, time2):
        # Credit for the core cleverness to Sharoon Thomas:
        # http://code.activestate.com/recipes/578113-human-readable-format-for-a-given-time-delta/
        delta = dateutil.relativedelta.relativedelta(time1, time2)
        attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
        statements = ['%d %s' % (getattr(delta, attr), getattr(delta, attr) != 1 and attr or attr[:-1]) for attr in attrs if getattr(delta, attr)]
        offset = ""
       	if len(statements) == 0:
            offset = "just now"
        else:
            if len(statements) > 1:
                 statements[-1] = "and {0}".format(statements[-1])
            offset = ", ".join(statements)
        return offset		

    def get_seen_record(self,who,channel):
        """Get seen record for specific user.

        :who: nickname of IRC user
        :channel channel IRC user was in
        """
        value = {}
        if channel in self:
            if who in self[channel]:
                value = self[channel][who]
        return value
    
    def update_seen_record(self,who,channel,message,time):
        """Update seen record for specific user.

        :who: nickname of IRC user
        :channel channel IRC user was in
        :message message IRC user last said
        :time time of last message

        """
        if channel in self:
            d = self[channel]
        else:
            d = { who : {} }
        d[who] = { "message" : message , "time" : time }
        self[channel] = d 

    def callback_message(self, msg):
        who = msg.frm.nick
        channel = None
        if hasattr(msg.to, 'room'):
            channel = msg.to.room
        message = msg.body
        time = datetime.datetime.now()
        if channel is not None:
	        self.update_seen_record(who,channel,message,time)

    def get_seen(self, msg, args):
    # Get user, get channel specifier
        who = None
        if len(args) >= 1:
            if len(args[0]) == 0:
                who = msg.frm.nick
            else:
                who = args[0]

        channel = None
        seen_record = {}
        if hasattr(msg.to, 'room'):
            channel = msg.to.room
        
        if who is not None:  
            result = "%s has never been seen" % (who)
        else:
            result = "Just exactly who are you looking for ?"

        if channel is not None and who is not None:
            seen_record = self.get_seen_record(who,channel)
        if seen_record:
            message = seen_record["message"]
            interval = self.human_readable_offset(datetime.datetime.now(),seen_record["time"])   
            result = "%s was last seen in %s %s saying %s" % (who,channel, interval,message)
        return result

    @botcmd(split_args_with = ' ')
    def seen(self, msg, args):
        """Command to show when user is last seen""" 
        result = self.get_seen(msg,args)
        return result 

