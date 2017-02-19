from errbot import BotPlugin, botcmd
from bs4 import BeautifulSoup
import requests

class Stream(BotPlugin):
    """Stream plugin for Errbot"""
    def activate(self):
        super().activate()
        self.value = { "ogv" : {} , "rtmp" : {} , "radio" : {} }

    # Existing stream bot 
    # get stream name
    # set stream name
    # get streamer name
    # set streamer name
    # get stream viewer count
    # unset stream name
    # We have two stream types OGV and RTMP, and maybe in the future we will have multiple channels
    # per stream type and also HLS streams 
    # subcommand streamtype value ? or separate commands ? 
   
    def gettopic(self,streamtype):
        topic = "Nothing streaming"
        if "stream" in self.value[streamtype] and "streamer" in self.value[streamtype]:
          topic  =  "Watch " + self.value[streamtype]["stream"] + " with " + self.value[streamtype]["streamer"]
        elif "stream" in self.value[streamtype] and "streamer" not in self.value[streamtype]: 
          topic  =  "Watch " + self.value[streamtype]["stream"] + " with an unknown Lainon" 
        elif "stream" not in self.value[streamtype] and "streamer" in self.value[streamtype]: 
          topic  =  "Watch an unknown stream with " + self.value[streamtype]["streamer"]
        return topic
        
    def changetopic(self,newtopic):
        room = self.query_room("#lainstream")
        room.topic = newtopic
    
    @botcmd(split_args_with = ' ')
    def stream(self, msg, args):
        """Get Stream name """
        name = "Nothing"
        streamtype  = "rtmp"       
        if len(args) == 1 and args[0] != "":
            streamtype = args[0]
        if streamtype in self.value:
            if "stream" in self.value[streamtype]:
                name = self.value[streamtype]["stream"] 
        result = "%s is streaming right now." % name
        return result 
    
    @botcmd(split_args_with = ' ')
    def streamset(self, msg, args):
        """Set Stream name """
        streamtype  = "rtmp"       
        name = None
        if len(args) == 1 and args[0] != "":
            name = args[0]
        elif len(args) >= 2:
            if args[0] == "radio" or args[0] == "ogv" or args[0] == "rtmp":
                streamtype = args[0]
                name = ' '.join(args[1:])
            else:
                name = ' '.join(args[0:])
        
        self.value[streamtype]["stream"] = name 
        result = "Okay, stream name set to %s" % name
        self.changetopic(self.gettopic(streamtype))
        return result
    
    @botcmd(split_args_with = ' ')
    def streamunset(self, msg, args):
        """Unset Stream name """
        result = "Stream name unset"
        streamtype  = "rtmp"       
        if len(args) == 1 and args[0] != "":
            streamtype = args[0]
        if streamtype in self.value:
            if "stream" in self.value[streamtype]:
                del self.value[streamtype]["stream"] 
        self.changetopic(self.gettopic(streamtype))
        return result

    @botcmd(split_args_with = ' ')
    def streamer(self, msg, args):
        """Get Streamer name """
        name = "Noone"
        streamtype  = "rtmp"       
        if len(args) == 1 and args[0] != "":
            streamtype = args[0]
        if streamtype in self.value:
            if "streamer" in self.value[streamtype]:
                name = self.value[streamtype]["streamer"] 
        result = "%s is streaming right now." % name
        return result 
    
    @botcmd(split_args_with = ' ')
    def streamerset(self, msg, args):
        """Set Streamer name """
        streamtype  = "rtmp"       
        name = None
        if len(args) == 1 and args[0] != "":
            name = args[0]
        elif len(args) >= 2:
            if args[0] == "radio" or args[0] == "ogv" or args[0] == "rtmp":
                streamtype = args[0]
                name = ' '.join(args[1:])
            else:
                name = ' '.join(args[0:])
        self.value[streamtype]["streamer"] = name 
        result = "Okay, streamer name set to %s" % name
        self.changetopic(self.gettopic(streamtype))
        return result
    
    @botcmd(split_args_with = ' ')
    def streamerunset(self, msg, args):
        """Unset Streamer name """
        result = "Streamer name unset"
        streamtype  = "rtmp"       
        if len(args) == 1 and args[0] != "":
            streamtype = args[0]
        if streamtype in self.value:
            if "streamer" in self.value[streamtype]:
                del self.value[streamtype]["streamer"] 
        self.changetopic(self.gettopic(streamtype))
        return result
    
    @botcmd(split_args_with = ' ')
    def viewers(self, msg, args):
        """Display viewers """
        streamtype  = "rtmp"       
        suffix = "" 
        viewers  = "no"
        if len(args) == 1 and args[0] != "":
            streamtype = args[0]
        if streamtype == "rtmp":
            suffix = "/live/subs?app=live&name=stream"
        else:
            suffix = "/radio_assets/status.xsl"

        url = "https://lainchan.org%s" % suffix 
        response = requests.get(url)
        soup = BeautifulSoup(response.content,"lxml")

        if streamtype == "rtmp":
            viewers = soup.find('p').text.strip()
        else:
           results = soup.find_all("td",class_="streamdata")
           offset = 0
           if streamtype == "ogv":
                offset = 22
           elif streamtype == "radio":
                 offset = 13
           if len(results) >= offset:
               viewers = results[offset].text.strip()
        result = "Stream has %s viewers" % viewers
        return result
 
