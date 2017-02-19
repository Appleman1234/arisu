from errbot import BotPlugin, botcmd
import datetime, pytz


class Time(BotPlugin):
    """Time plugin for Errbot"""

    def find_tz(self,place):
        for x in pytz.all_timezones_set:
            if place in x:
                return x
        return None

    def get_time_for_timezone(self,timezone_name):
        fmt = '%Y-%m-%d %H:%M:%S %Z %z'
        tz = pytz.timezone(timezone_name)
        local_time = datetime.datetime.now(tz)
        return local_time.strftime(fmt)

    @botcmd(split_args_with = ' ')
    def time(self, msg, args):
        """Time with timezone or location as parameter"""
        if not args:
            return 'Am I supposed to guess the location?...'
        if len(args) == 1 and args[0].lower() == 'utc':
            tz_name = 'UTC'
        elif len(args) == 1:
            place = args[0] 
            tz_name = self.find_tz(place)
        else:
            place = '_'.join([word.capitalize() for word in args])
            tz_name = self.find_tz(place)

        if not tz_name:
            result = 'Sorry cannot find the timezone for this location'   
        else:
            result = self.get_time_for_timezone(tz_name)
        return result 

    @botcmd
    def jtime(self, msg, args):
        """Time in Japan"""
        result = self.get_time_for_timezone("Asia/Tokyo")
        return result 

    @botcmd
    def utime(self, msg, args):
        """Time in UTC"""
        result = self.get_time_for_timezone("UTC")
        return result 
