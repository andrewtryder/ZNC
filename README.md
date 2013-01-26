Supybot-ZNC
===========

Supybot plugin to support ZNC auto-op plugin/module.

Currently, this is not yet working. 

Disclaimer

    First, I can't emphasize enough the dangers of any type of auto-op system. Passwords get stolen
    or hacked, hosts have, at times, been spoofed or forged, etc. If you're paranoid, don't run this.
    The storage system uses plain-text for this module so, unless this is run on a secure and dedicated
    box, it's not secure. ZNC's module is the same so, again, even with the hostmask matching with
    challenge, do not consider this secure.
    
Background

    ZNC, the awesome IRC bouncer, includes an *autoop module that was designed to work between clients.
    Someone did great work to port this over to TCL (vomit) so that it can work on Eggdrop bots. I decided
    to do the same for Supybot/Limnoria. Their challenge/response system is described on here:
    
    http://wiki.znc.in/Autoop
    
    
