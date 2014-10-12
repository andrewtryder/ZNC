[![Build Status](https://travis-ci.org/reticulatingspline/ZNC.svg?branch=master)](https://travis-ci.org/reticulatingspline/ZNC)

# Limnoria plugin for ZNC's autoop module.

## Introduction

I consider this plugin BETA. It works for me but I'm sure with the nature of a plugin like this
that some things are broken.

First, I can't emphasize enough the dangers of any type of auto-op system. Passwords get stolen
or hacked, hosts have, at times, been spoofed or forged, etc. If you're paranoid, don't run this.
The storage system uses plain-text for this module so, unless this is run on a secure and dedicated
box, it's not secure. ZNC's module is the same so, again, even with the hostmask matching with
challenge, do not consider this secure.

ZNC, the awesome IRC bouncer, includes an autoop module that was designed to work between clients.

http://wiki.znc.in/Autoop

Someone did great work to port this over to TCL (vomit) so that it can work on Eggdrop bots. I decided
to do the same for Supybot/Limnoria.


Grab plugin and load. You will need to then need to add matching users on both the bot and ZNC client.

As both are similar beyond their commands, you basically add a user that matches the other client/hostmask
with the same key and channel. I've tested this with ZNC 1.0 and the latest version of Limnoria.

NOTE: I did NOT implement the __NOKEY__ feature (essentially auto-op for clients not running ZNC)
from the ZNC autoop module because there are other ways to do such a thing, like with AutoMode, already in Supybot.
I have no plans either as it would require a rewrite of some major parts. 

## Install

You will need a working Limnoria bot on Python 2.7 for this to work.

Go into your Limnoria plugin dir, usually ~/supybot/plugins and run:

```
git clone https://github.com/reticulatingspline/ZNC
```

To install additional requirements, run:

```
pip install -r requirements.txt 
```

Next, load the plugin:

```
/msg bot load ZNC
```

Now, you will need to configure a user and mate it up with your autoop config.

## Example Usage 

(Must be in priv msg and as at least an admin on the bot where it is an op in #channel.)

```
<spline> zncadduser spline *!*spline@*host.mask key #channel 
<myybot> OK
<spline> znclistusers
<myybot> +------------+------------------------------------------+-----------------+----------------------+
<myybot> | USERNAME   | HOSTMASK                                 | KEY             | CHANNEL              |
<myybot> +------------+------------------------------------------+-----------------+----------------------+
<myybot> | spline     | *!*spline@*host.mask                     | key             | #channel             |
<myybot> +------------+------------------------------------------+-----------------+----------------------+
<spline> zncremoveuser spline
<myybot> OK
```

## About

All of my plugins are free and open source. When I first started out, one of the main reasons I was
able to learn was due to other code out there. If you find a bug or would like an improvement, feel
free to give me a message on IRC or fork and submit a pull request. Many hours do go into each plugin,
so, if you're feeling generous, I do accept donations via Amazon or browse my [wish list](http://amzn.com/w/380JKXY7P5IKE).

I'm always looking for work, so if you are in need of a custom feature, plugin or something bigger, contact me via GitHub or IRC