# -*- coding: utf-8 -*-
###
# Copyright (c) 2013-2014, spline
# All rights reserved.
#
#
###

# additional
import time  # challenges
from collections import defaultdict  # challenges
import hashlib  # md5
from random import choice  # md5
import re  # regex
import csv  # db
# addt'l supybot
import supybot.ircmsgs as ircmsgs
import supybot.conf as conf
import supybot.schedule as schedule
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
        self._channels = {}
        self._challenges = defaultdict(dict)
        self._openUsers()

    def die(self):
        self._flushUsers()
        self.__parent.die()

    #####################
    # INTERNAL DATABASE #
    #####################

    def _flushUsers(self):
        """Writes the ZNC DB to the system."""
        fd = utils.file.AtomicFile(self.filename)
        writer = csv.writer(fd)
        for (username, entry) in self._users.iteritems():
            for (hostmask, key, channel) in entry:
                writer.writerow([username, hostmask, key, channel])
        fd.close()

    def _openUsers(self):
        """Opens up the ZNC DB from the system."""
        try:
            fd = file(self.filename)
        except EnvironmentError, e:
            self.log.warning("Couldn't open %s: %s", self.filename, e)
            return
        reader = csv.reader(fd)
        for (username, hostmask, key, channel) in reader:
            self._addUser(username, hostmask, key, channel)
        fd.close()

    def _addUser(self, username, hostmask, key, channel):
        """Adds user to ZNC cache."""
        self._users[username] = [(hostmask, key, channel)]
        self._popUserCache()
        self._flushUsers()

    def _popUserCache(self):
        """Populate _channels cache."""
        users = self._users.items()
        if users:
            self._channels.clear()
            for (k, v) in users:
                self._channels.setdefault(v[0][2], []).append((v[0][0], k))

    ###################################
    # DATABASE PUBLIC ADMIN FUNCTIONS #
    ###################################

    def znclistusers(self, irc, msg, args):
        """
        Display all ZNC users. Must be run in private message.
        NOTICE: I must be run via private message by an admin.
        """

        if irc.isChannel(ircutils.toLower(msg.args[0])):
            irc.reply("ERROR: I must be run via private message by an admin.")
            return
        users = self._users.items()
        if users:
            irc.reply("+------------+------------------------------------------+-----------------+----------------------+")
            irc.reply("| {0:10} | {1:40} | {2:15} | {3:20} |".format('USERNAME', 'HOSTMASK', 'KEY', 'CHANNEL'))
            irc.reply("+------------+------------------------------------------+-----------------+----------------------+")
            for (k, v) in users:
                irc.reply("| {0:10} | {1:40} | {2:15} | {3:20} |".format(k, v[0][0], v[0][1], v[0][2]))
            irc.reply("+------------+------------------------------------------+-----------------+----------------------+")
        else:
            irc.reply("I have no ZNC users.")

    znclistuser = wrap(znclistusers, [('checkCapability', 'admin')])

    def zncadduser(self, irc, msg, args, username, hostmask, key, channel):
        """<username> <hostmask> <key> <channel>
        Add a user to the ZNC auto-op database. Ex: user1 *!*user@hostmask.com passkey #channel
        NOTICE: I must be run via private message by an admin.
        """

        if irc.isChannel(ircutils.toLower(msg.args[0])):
            irc.reply("ERROR: I must be run via private message by an admin.")
            return
        if username in self._users:  # do our checks now to see if we can add.
            irc.reply("ERROR: I already have a user: {0}".format(username))
            return
        if not ircutils.isChannel(channel):  # make sure the channel is valid.
            irc.reply("ERROR: {0} is not a valid channel".format(channel))
            return
        if not ircutils.isUserHostmask(hostmask):  # make sure hostmask is valid.
            irc.reply("ERROR: {0} is not a valid hostmask.".format(hostmask))
            return
        if len(self._users) > 0:  # make sure we have users to check against.
            failcheck = False
            for (k, v) in self._users.items():  # check the hostnames.
                userhostname, userkey, userchannel = v[0]
                if ircutils.hostmaskPatternEqual(hostmask, userhostname) and channel == userchannel:
                    irc.reply("ERROR: I cannot add {0}. Hostmask {1} matches the hostmask {2} in existing user: {3} for {4}".format(username, hostmask, userhostname, k, channel))
                    failcheck = True
                    break
        # check if hostname passed.
        if failcheck:
            return
        # username and hostmask are clean. lets add.
        try:
            self._addUser(username, hostmask, key, channel)
            irc.replySuccess()
        except ValueError, e:
            irc.reply("Error adding {0} :: {1}".format(username, e))

    zncadduser = wrap(zncadduser, [('checkCapability', 'admin'), ('somethingWithoutSpaces'), ('somethingWithoutSpaces'), ('somethingWithoutSpaces'), ('somethingWithoutSpaces')])

    def zncremoveuser(self, irc, msg, args, username):
        """<username>
        Delete a user from the ZNC auto-op database.
        NOTICE: I must be run via private message by an admin.
        """

        if irc.isChannel(ircutils.toLower(msg.args[0])):
            irc.reply("ERROR: I must be run via private message by an admin.")
            return
        try:
            del self._users[username]
            self._popUserCache()
            self._flushUsers()
            irc.replySuccess()
        except KeyError:
            irc.reply('ERROR: There is no userid: %s' % username)

    zncremoveuser = wrap(zncremoveuser, [('checkCapability', 'admin'), ('somethingWithoutSpaces')])

    def zncprintcache(self, irc, msg, args):
        irc.reply("Channels: {0}".format(self._channels))
    zncprintcache = wrap(zncprintcache)

    ######################
    # INTERNAL FUNCTIONS #
    ######################

    def _zncchallenge(self):
        """ Return a valid ZNC CHALLENGE string with 32-character string. """
        challenge = map(lambda i: choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?.,:;/*-+_()"), range(32))
        randomchallenge = "".join(challenge)
        return randomchallenge

    def _zncresponse(self, key, challenge):
        """ Return a valid ZNC RESPONSE string using matching key and challenge. """
        response = hashlib.md5(key + "::" + challenge).hexdigest()
        return response

    ############
    # TRIGGERS #
    ############
    def doNotice(self, irc, msg):
        mynick = irc.nick
        user = msg.nick
        hostname = irc.state.nickToHostmask(user)
        (recipients, text) = msg.args
        if ircmsgs.isCtcp(msg) or ircmsgs.isAction(msg) or irc.isChannel(msg.args[0]):  # ignore obvious non.
            return
        elif text.startswith('!ZNCAO'):  # we only process notices with !ZNCAO.
            textparts = text.split()  # split. should be 3.
            if len(textparts) != 3:  # make sure we have 3 parts to a valid ZNC message.
                self.log.error("ERROR: ZNC notice from {0} is malformed. I got: {1}".format(user, text))
                return
            if textparts[0] == "!ZNCAO" and textparts[1] == "CHALLENGE":  # if user is opped and we are not. we get challenge.
                self.log.info("We got a ZNC challenge from {0}".format(user))
                challenge = textparts[2]
                for (key, value) in self._users.items():  # iterate now through our users for key.
                    hostmask, key, channel = value[0]
                    if ircutils.hostmaskPatternEqual(hostmask, hostname):  # if we have a match.
                        if not irc.state.channels[channel].isOp(mynick) and irc.state.channels[channel].isOp(user):  # and they're opped, we're not.
                            response = "!ZNCAO RESPONSE {0}".format(self._zncresponse(key, challenge))  # this key and the challenge.
                            self.log.info("Sending {0} {1}".format(user, response))
                            irc.queueMsg(ircmsgs.notice(user, response))
            elif textparts[0] == "!ZNCAO" and textparts[1] == "RESPONSE":  # means we sent a challenge. we're opped, user is not.
                self.log.info("We got a ZNC response from {0}".format(user))
                if user in self._challenges:  # user is in challenges because their hostname matched.
                    for chan in self._challenges[user]:
                        if irc.state.channels[chan].isOp(mynick) and not irc.state.channels[chan].isOp(user):  # im op. they're not.
                            (chaltime, challenge, chaluser) = self._challenges[user][chan]
                            if chaltime - time.time() < 60:  # challenge less than 60s ago.
                                hostmask, key, channel = self._users[chaluser][0]  # find the user in the db.
                                mychallenge = self._zncresponse(key, challenge)  # create my own based on challenge/key to auth.
                                if mychallenge == textparts[2]:  # compare my md5 hash and theirs.
                                    self.log.info("Giving ZNC OP to {0} on {1} after valid key matching.".format(user, chan))
                                    irc.queueMsg(ircmsgs.op(chan, user))  # op if they're valid.
                                else:  # invalid key.
                                    self.log.info("ERROR: Invalid key from: {0} on {1}".format(user, chan))
                            else:  # key is too old.
                                self.log.info("ERROR: {0} in {1} challenge was more than 60s ago.".format(user, chan))
                else:
                    self.log.info("ERROR: {0} not found in ZNC challenges.".format(user))

    # if not irc.state.channels[channel].synchro:

    def doJoin(self, irc, msg):
        channel = ircutils.toLower(msg.args[0])
        mynick = irc.nick
        user = msg.nick
        hostname = irc.state.nickToHostmask(user)
        if not ircutils.strEqual(irc.nick, msg.nick):  # not me joining.
            if channel in self._channels.keys():  # do we have a matching channel?
                if irc.state.channels[channel].isOp(mynick):  # am I an op?
                    for (hostmask, username) in self._channels[channel]:
                        if ircutils.hostmaskPatternEqual(hostmask, hostname):  # do we have a matching user?
                            self.log.info("{0} matched {1} in {2} on username {3}. Sending ZNC challenge.".format(hostmask, user, channel, username))
                            challenge = self._zncchallenge()
                            self._challenges[user][channel] = (time.time() + 60, challenge, username)
                            challenge = "!ZNCAO CHALLENGE {0}".format(challenge)
                            def sendNotice():  # for the delayed send.
                                irc.queueMsg(ircmsgs.notice(user, challenge))
                            schedule.addEvent(sendNotice, (time.time() + choice(range(2, 6))))
                            break

Class = ZNC


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=250:
