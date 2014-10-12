###
# Copyright (c) 2013-2014, spline
# All rights reserved.
#
#
###

from supybot.test import *

class ZNCTestCase(PluginTestCase):
    plugins = ('ZNC',)
    
    def testZNC(self):
        # zncadduser, znclistusers, zncprintcache, and zncremoveuser
        self.assertResponse("zncadduser spline *!*spline@*host.mask key #test", "The operation succeeded.")
        self.assertResponse("zncremoveuser spline", "The operation succeeded.")


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
