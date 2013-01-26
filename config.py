###
# Copyright (c) 2013, spline
# All rights reserved.
#
#
###

import supybot.conf as conf
import supybot.registry as registry
from supybot.i18n import PluginInternationalization, internationalizeDocstring

_ = PluginInternationalization('ZNC')

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('ZNC', True)


ZNC = conf.registerPlugin('ZNC')
conf.registerGlobalValue(ZNC,'channels',registry.String('', _("""Channels to operate it in.""")))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=150:
