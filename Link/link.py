from errbot.backends.irc import IRCRoom
from errbot import BotPlugin, botcmd,  re_botcmd
from itertools import chain
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import eventlet
import re
import requests
eventlet.monkey_patch()

# Regex is from last comment of https://gist.github.com/gruber/249502 , in order to match gitlai.in domain name etc 
link_regex = re.compile('((?:[a-z][\w-]+:(?:\/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}\/?)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\)){0,}(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s\!()\[\]{};:\'\"\.\,<>?«»“”‘’]){0,})')

class Link(BotPlugin):
    """Link plugin for Errbot"""

    def callback_message(self, msg):
        who = msg.frm.nick
        channel = None
        if hasattr(msg.to, 'room'):
            channel = msg.to.room
        message = msg.body
        matches = re.findall(link_regex,message)
        return_message = ""
        for match in matches:
            url = match[0]
            parsed_url = urlparse(url)
            if len(parsed_url.scheme) == 0:
                url = "https://" + url 
            self.log.error("URL: " + url)
            noembed = requests.get('https://noembed.com/embed', params={'url': url}, verify=False,timeout=30)
            resp = noembed.json()
            if 'error' not in resp.keys():
                return_message += resp['title'].strip() + "\r\n"
            else:
                head = requests.head(url)
                max_size = 5e6
                if 'content-length' in head.headers and  int(head.headers['content-length']) > max_size:
                    return_message = "File too big for link preview\r\n"
                else:
                    with eventlet.Timeout(60, False):
                        response = requests.get(url,timeout=30)
                        if response.status_code == 200:
                            if 'text/html' in response.headers['content-type']:
                                soup = BeautifulSoup(response.content,"lxml")
                                return_message += soup.title.string + "\r\n"
                            else:
                                return_message += response.headers['content-type'] + " Size: " + response.headers['content-length'] + "\r\n"
        if len(return_message) > 0:
            self.send(msg.to, return_message)	
