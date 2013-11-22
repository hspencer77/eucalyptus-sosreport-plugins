## Copyright (C) 2013 Eucalyptus Systems, Inc.

### This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import sos.plugintools
import os

class eucaconsole(sos.plugintools.PluginBase):
    """Eucalyptus Cloud - Console
    """
    def checkenabled(self):
        if self.isInstalled("eucalyptus-console"):
            return True
        return False

    def setup(self):
        """
        Grabs the following regarding the Eucalyptus Console:
            - configuration file under /etc/eucalyptus-console
            - log file location under /var/log/eucalyptus-console directory
        """
        self.addCopySpec("/etc/eucalyptus-console")
        """
        Check to see if /var/log/eucalyptus-console exists - this was a change for Eucalyptus 3.4.0-1
        If it doesn't exists, then the Eucalyptus User Console logs will be in /var/log/messages
        """
        if os.path.exists('/var/log/eucalyptus-console'):
            self.addCopySpec("/var/log/eucalyptus-console/*")
        return
