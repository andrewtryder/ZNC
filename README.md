Supybot-ZNC
===========

Supybot plugin to support ZNC autoop plugin/module.


Disclaimer

    First, I can't emphasize enough the dangers of any type of auto-op system. Passwords get stolen
    or hacked, hosts have, at times, been spoofed or forged, etc. If you're paranoid, don't run this.
    The storage system uses plain-text for this module so, unless this is run on a secure and dedicated
    box, it's not secure. ZNC's module is the same so, again, even with the hostmask matching with
    challenge, do not consider this secure.

Background

    ZNC, the awesome IRC bouncer, includes an autoop module that was designed to work between clients.

    http://wiki.znc.in/Autoop

    Someone did great work to port this over to TCL (vomit) so that it can work on Eggdrop bots. I decided
    to do the same for Supybot/Limnoria.

Instructions

    Grab plugin and load. You will need to then need to add matching users on both the bot and ZNC client.

    As both are similar beyond their commands, you basically add a user that matches the other client/hostmask
    with the same key and channel. I've tested this with ZNC 1.0 and the latest version of Limnoria.

    See: zncadduser / znclistusers

Warnings

    I cannot emphasize what I said under the disclaimer enough. People think because this issues a challenge,
    instead of just matching a channel/hostmask, that it is secure. It is not. I recommend this for small channels
    where you don't have a botnet ready
