# Copyright (C) 2013 Eucalyptus Systems, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os
try:
    from sos.plugins import Plugin, RedHatPlugin
    object = ['Plugin', 'RedHatPlugin']
except ImportError:
    import sos.plugintools
    object = ['sos.plugintools.PluginBase']


class eucaconsole(object):
    """Eucalyptus Cloud - Console
    """
    def checkenabled(self):
        if (
            self.isInstalled("eucalyptus-console") or
            self.isInstalled("eucaconsole")
        ):
            return True
        return False

    def setup(self):
        """
        Grabs the following regarding the Eucalyptus Console:
            - configuration file under /etc/eucalyptus-console
            - log file location under /var/log/eucalyptus-console directory
        """
        if self.isInstalled("eucalyptus-console"):
            self.addCopySpec("/etc/eucalyptus-console")
            """
            Check if /var/log/eucalyptus-console exists (Eucalyptus 3.4.0-1)
            If not present, then Console logs are in /var/log/messages
            """
            if os.path.exists('/var/log/eucalyptus-console'):
                self.addCopySpec("/var/log/eucalyptus-console/*")
        else:
            """
            Grab following for Eucalyptus Console
            - config file under /etc/eucaconsole
            - log file /var/log/eucaconsole.log
            """
            self.addCopySpec("/etc/eucaconsole")
            self.addCopySpec("/var/log/eucaconsole.log*")
        return
