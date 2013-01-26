# -*- coding: utf-8 -*-
###
# Copyright (c) 2013, spline
# All rights reserved.
#
#
###

# additional
import hashlib # md5
import string # md5
from random import choice # md5
import re # regex
import csv # db
# addt'l supybot
import supybot.ircmsgs as ircmsgs
import supybot.ircdb as ircdb
import supybot.conf as conf
# stock
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization, internationalizeDocstring

_ = PluginInternationalization('ZNC')

@internationalizeDocstring
class ZNC(callbacks.Plugin):
    """Add the help for "@plugin help ZNC" here
    This should describe *how* to use this plugin."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(ZNC, self)
        self.__parent.__init__(irc)
        self._users = ircutils.IrcDict()
        self.filename = conf.supybot.directories.data.dirize('ZNC.db')
        self._openUsers()
        self._channels = []
 
    def die(self):
        self._flushUsers()
        self.__parent.die()

    #####################
    # INTERNAL DATABASE #
    #####################
    
    def _flushUsers(self):
        fd = utils.file.AtomicFile(self.filename)
        writer = csv.writer(fd)
        # notes
        for (username, entry) in self._users.iteritems():
            for (hostmask, key, channel) in entry:
                writer.writerow([username, hostmask, key, channel])
        fd.close()

    def _openUsers(self):
        try:
            fd = file(self.filename)
        except EnvironmentError, e:
            self.log.warning('Couldn\'t open %s: %s', self.filename, e)
            return
        reader = csv.reader(fd)
        for (username, hostmask, key, channel) in reader:
            self._addUser(username, hostmask, key, channel)
        fd.close()

    def _addUser(self, username, hostmask, key, channel):
        self._users[username] = [(hostmask, key, channel)]
        self._flushUsers()

    ###################################
    # DATABASE PUBLIC ADMIN FUNCTIONS #
    ###################################
    
    def znclistusers(self, irc, msg, args):
            users = self._users.items()
            if users:
                for i,(k,v) in users:
                    if count == 0:
                        irc.reply("{0} {1}".format(k,v))
                    else:
                        irc.reply("{0} {1}".format(k,v))
            else:
                irc.reply("I have no ZNC users.")
    znclistuser = wrap(znclistusers, [('checkCapability', 'admin')])
      
    def zncadduser(self, irc, msg, args, username, hostmask, key, channel):
        try:
            self._addUser(username, hostmask, key, channel)
            irc.replySuccess()
        except ValueError, e:
            irc.reply("Error adding {0} :: {1}".format(username, e))            
    zncadduser = wrap(zncadduser, [('checkCapability', 'admin'), ('somethingWithoutSpaces'), ('somethingWithoutSpaces'), ('somethingWithoutSpaces'), ('somethingWithoutSpaces')])

    def zncremoveuser(self, irc, msg, args, username):
        try:
            del self._users[username]
            self._flushUsers()
            irc.replySuccess()
        except KeyError:
            irc.error('There was no userid: %s' % uid)
    zncremoveuser = wrap(zncremoveuser, [('checkCapability', 'admin'), ('somethingWithoutSpaces')])
    
    ######################
    # INTERNAL FUNCTIONS #
    ######################
    
    def _md5(self, string):
        """ Return a md5 hashed string. """
        return hashlib.md5(string).hexdigest()
    
    def _zncchallenge(self):
        """ Return a valid ZNC CHALLENGE string with 32-character string. """
        challenge = map(lambda i: choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?.,:;/*-+_()"), range(32))
        randomchallenge = string.join(challenge, "")
        s = "!ZNCAO CHALLENGE {0}".format(randomchallenge)
        return s
            
    def _zncresponse(self, key, challenge):
        """ Return a valid ZNC RESPONSE string using matching key and challenge. """
        response = self._md5(key + "::" + challenge)
        s = "!ZNCAO RESPONSE {0}".format(response)
        return s

    ############
    # TRIGGERS #
    ############
    
    def doNotice(self, irc, msg):
        channel = msg.args[0].lower()
        mynick = irc.nick
        user = msg.nick
        hostname = irc.state.nickToHostmask(user)
        (recipients, text) = msg.args
        if ircmsgs.isCtcp(msg) or ircmsgs.isAction(msg) or irc.isChannel(channel):
            return
        elif text.startswith('!ZNCAO'):
            self.log.info("{0} {1}".format(user, text))
            textparts = text.split()
            if textparts[0] == "!ZNCAO" and textparts[1] == "CHALLENGE":
                self.log.info("We got a challenge {0}".format(text))
                challenge = textparts[2]
                response = self._zncresponse(self.key, challenge)
                self.log.info("Sending {0} {1}".format(user, response))
                irc.queueMsg(ircmsgs.notice(user, response))             
            elif textparts[0] == "!ZNCAO" and textparts[1] == "RESPONSE":
                self.log.info("We got a response {0}".format(text))
        else:
            return

    # challenge autoop users when they join.
    
    #irc.queueMsg(ircmsgs.mode(channel, ['+o %s'])
    def doJoin(self, irc, msg):
        # get some things to process before we start.
        channel = msg.args[0].lower()
        mynick = irc.nick
        user = msg.nick
        ident = ircutils.userFromHostmask(msg.prefix)
        # (nick, user, host) = ircutils.splitHostmask(hostmask)
        hostname = irc.state.nickToHostmask(user)
        if ircutils.strEqual(irc.nick, msg.nick): # is it me joining?
            return
        # next, check if the channel is in one of those we watch.
        channels = self.registryValue('channels').split(',')
        # randomDelay = choice(range(2,6))
        if channel == "#supybot":
            if not irc.state.channels[channel].isOp(mynick): # am I an op?
                self.log.info("I am not an op in {0}.".format(channel))
                return
            if ircutils.hostmaskPatternEqual(self.hostmask, hostname):
                self.log.info("{0} matched {1} in {2}".format(self.hostmask, user, channel))
            else:
                self.log.info("{0} did not match {1} in {2}".format(self.hostmask,user,channel))
       
Class = ZNC


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=250:
