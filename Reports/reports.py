# coding=utf8
from errbot import BotPlugin, botcmd
import MySQLdb as mdb
import time
import pprint

class Reports(BotPlugin):
    """Reporter plugin for Errbot"""
    
    def get_configuration_template(self):
        return {'PASSWORD': 'password','USERNAME':'username', 'DATABASE' : 'database'}

    def get_thread_for_post(self, post,board):
        thread = ""
        cur = self.connection.cursor(mdb.cursors.DictCursor)
        query = "SELECT thread from posts_%s where id = %s" % (board , post)
        row = None
        if board is not None:
            cur.execute(query) 
            row = cur.fetchone()
        if row is None:
            thread = post
        else:
            if row['thread'] is not None:
                thread = row['thread']
            else:
                thread = post
        return thread


    def update_reports(self):
        cur = self.connection.cursor(mdb.cursors.DictCursor)
        cur.execute("SELECT * from reports") 
        rows = cur.fetchall()
        for row in rows:
            report = dict()
            report["id"] = row["id"]
            report["time"] = row["time"]
            report["ip"] = row["ip"]
            report["board"] = row["board"]
            report["post"] = row["post"]
            report["reason"] = row["reason"]
            report["url"] = "https://lainchan.org/mod.php?/%s/res/%s.html#%s" % (report['board'], self.get_thread_for_post(report["post"] ,report["board"] ) ,report['post']) 
            report["intable"] = True 
            report["reported"] = False 
            self.reports[row["id"]] = report
        
        for report in self.reports:
            if self.reports[report]["intable"] == True and self.reports[report]["reported"] == False:
                diff = time.time() - int(self.reports[report]["time"])
                if diff < 60:
                    room = self.build_identifier('#staff')   
                    message = self.reports[report]["url"] + " " + self.reports[report]["reason"]
                    self.send(room,message)
                    self.reports[report]["reported"] = True


    def activate(self):
        super().activate()
        self._bot.conn.send_private_message("ChanServ","invite #staff") 
        self.reports = dict()
        self.connection = mdb.connect('mysql', self.config['USERNAME'], self.config['PASSWORD'], self.config['DATABASE'],charset='utf8');
        self.start_poller(60, self.update_reports)

    def deactivate(self):
        super().deactivate()
        self.connection.close()

    @botcmd(split_args_with = ' ')
    def reports(self, msg, args):
        """Gets reported posts from Lainchan"""
        result =  "Reports: \n"
        for report in self.reports:
            if self.reports[report]["intable"] == True:
                message = self.reports[report]["url"] + " " + self.reports[report]["reason"] + "\n"
                result += message
        return result 

    @botcmd(split_args_with = ' ')
    def dismiss(self, msg, args):
        """dismiss posts from Lainchan"""
        result =  "dissmis output goes here"
        return result 
