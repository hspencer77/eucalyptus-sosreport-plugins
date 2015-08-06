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
import glob
try:
    from sos.plugins import Plugin, RedHatPlugin
    object = ['Plugin', 'RedHatPlugin']
except ImportError:
    import sos.plugintools
    object = ['sos.plugintools.PluginBase']


class eucacore(object):

    """Eucalyptus Cloud - Core
    """

    def checkenabled(self):
        if self.isInstalled("eucalyptus"):
            return True
        return False

    def setup(self):
        self.addCopySpec("/etc/eucalyptus")
        self.addCopySpec("/var/log/eucalyptus/*")
        self.addCopySpec("/var/lib/eucalyptus/keys")
        if os.path.isfile('/usr/bin/sha1sum'):
            self.collectExtOutput("find /var/lib/eucalyptus/keys \
                                  -type f -print | xargs -I {} sha1sum {}",
                                  suggest_filename="sha1sum-eucalyptus-keys")
        hprof_list = glob.glob('/var/log/eucalyptus/*.hprof')
        if hprof_list:
            self.collectExtOutput("rm -rf /var/log/eucalyptus/*.hprof",
                                  suggest_filename="hprof-removal")
        if os.path.isfile('/sbin/iptables-save'):
            self.collectExtOutput("/sbin/iptables-save --counters",
                                  suggest_filename="iptables-save-counters")
        if os.path.isfile('/sbin/ebtables-save'):
            self.collectExtOutput("/sbin/ebtables-save --counters",
                                  suggest_filename="ebtables-save-counters")
        if os.path.isfile('/usr/sbin/ipset'):
            self.collectExtOutput("/usr/sbin/ipset -s -o xml save",
                                  suggest_filename="ipset-xml-save")
        if os.path.isfile('/etc/pki/tls/certs/eucalyptus-enterprise.crt'):
            self.collectExtOutput("openssl x509 -text -in "
                                  + "/etc/pki/tls/certs/eucalyptus"
                                  + "-enterprise.crt"
                                  + " | grep -A 2 Validity",
                                  suggest_filename="euca-enterprise-cert"
                                  + "-validity")
            self.collectExtOutput("openssl x509 -text -in "
                                  + "/etc/pki/tls/certs/eucalyptus"
                                  + "-enterprise.crt"
                                  + " | grep -A 14 X509v3",
                                  suggest_filename="euca-enterprise-cert"
                                  + "-compliance")
        # check /tmp dir for sane owner/group/mode
        # mode '1777' also checks for sticky bit
        mode = os.stat("/tmp")
        if ((mode.st_uid != 0)
                or (mode.st_gid != 0)
                or (oct(mode.st_mode)[-4:] != '1777')):
            self.collectExtOutput("/bin/ls -ld /tmp",
                                  suggest_filename="tmp-dir-mode-fail")
        # gather a recursive listing of /var/lib/eucalyptus, including
        # dot-files
        if os.path.exists('/var/lib/eucalyptus'):
            self.collectExtOutput("/bin/ls -laR /var/lib/eucalyptus",
                                  suggest_filename="ls-laR-var-lib-eucalyptus")
        return
