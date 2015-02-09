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

import sos.plugintools
import os
import subprocess


class eucadb(sos.plugintools.PluginBase):
    """Eucalyptus Cloud - PostgreSQL
    """

    def checkenabled(self):
        if (self.isInstalled("postgresql91") and
           self.isInstalled("postgresql91-server") and
           self.isInstalled("eucalyptus-cloud")):
            return True
        return False

    def check_postgres(self):
        """
        Check postgres process using pgrep (eucalyptus-cloud controls it)
        """
        postgres_pgrep_cmd = ["/usr/bin/pgrep", "postgres"]
        try:
            postgres_chk, unused_val = subprocess.Popen(
                postgres_pgrep_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).communicate()
        except OSError, e:
            if 'No such' in e.strerror:
                self.addDiagnose("Error checking postgres process status")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e)

        if postgres_chk:
            for proc in postgres_chk.splitlines():
                if not proc:
                    raise
                else:
                    self.addDiagnose("Postgres is running: " + proc + ".")
        else:
            self.addDiagnose("Error checking postgres process status")
            print "### postgres/eucalyptus-cloud  doesn't seem to be running."
            raise
        return True

    def setup(self):
        if (
            os.path.isfile('/usr/pgsql-9.1/bin/pg_dump')
            and self.check_postgres()
        ):
            self.collectExtOutput(
                "/usr/pgsql-9.1/bin/pg_dump -c -o -h \
                 /var/lib/eucalyptus/db/data -p 8777 -U root eucalyptus_auth",
                suggest_filename="eucalyptus_auth.sql",
                timeout=600
            )
            self.collectExtOutput(
                "/usr/pgsql-9.1/bin/pg_dump -c -o -h \
                 /var/lib/eucalyptus/db/data -p 8777 -U root eucalyptus_cloud",
                suggest_filename="eucalyptus_cloud.sql",
                timeout=600
            )
            self.collectExtOutput(
                "/usr/pgsql-9.1/bin/pg_dump -c -o -h \
                 /var/lib/eucalyptus/db/data -p 8777 \
                 -U root eucalyptus_config",
                suggest_filename="eucalyptus_config.sql",
                timeout=600
            )
            self.collectExtOutput(
                "/usr/pgsql-9.1/bin/pg_dump -c -o -h \
                 /var/lib/eucalyptus/db/data -p 8777 -U root eucalyptus_dns",
                suggest_filename="eucalyptus_dns.sql",
                timeout=600
            )
            self.collectExtOutput(
                "/usr/pgsql-9.1/bin/pg_dump -c -o -h \
                 /var/lib/eucalyptus/db/data -p 8777 -U root database_events",
                suggest_filename="database_events.sql",
                timeout=600
            )
            self.collectExtOutput(
                "/usr/pgsql-9.1/bin/pg_dump -c -o -h \
                 /var/lib/eucalyptus/db/data -p 8777 \
                 -U root eucalyptus_faults",
                suggest_filename="eucalyptus_faults.sql",
                timeout=600
            )
            self.collectExtOutput(
                "/usr/pgsql-9.1/bin/pg_dump -c -o -h \
                 /var/lib/eucalyptus/db/data -p 8777 \
                 -U root eucalyptus_general",
                suggest_filename="eucalyptus_general.sql",
                timeout=600
            )
            self.collectExtOutput(
                "/usr/pgsql-9.1/bin/pg_dump -c -o -h \
                 /var/lib/eucalyptus/db/data -p 8777 \
                 -U root eucalyptus_records",
                suggest_filename="eucalyptus_records.sql",
                timeout=600
            )
            self.collectExtOutput(
                "/usr/pgsql-9.1/bin/pg_dump -c -o -h \
                 /var/lib/eucalyptus/db/data -p 8777 -U root \
                 --exclude-table=reporting_instance_usage_events \
                 eucalyptus_reporting",
                suggest_filename="eucalyptus_reporting.sql",
                timeout=600
            )
            self.collectExtOutput(
                "/usr/pgsql-9.1/bin/pg_dump -c -o -h \
                 /var/lib/eucalyptus/db/data -p 8777 -U \
                 root eucalyptus_storage",
                suggest_filename="eucalyptus_storage.sql",
                timeout=600
            )
            self.collectExtOutput(
                "/usr/pgsql-9.1/bin/pg_dump -c -o -h \
                 /var/lib/eucalyptus/db/data -p 8777 -U \
                 root eucalyptus_walrus",
                suggest_filename="eucalyptus_walrus.sql",
                timeout=600
            )
            if self.isInstalled("eucalyptus-enterprise-vmware-broker"):
                self.collectExtOutput(
                    "/usr/pgsql-9.1/bin/pg_dump -c -o -h \
                     /var/lib/eucalyptus/db/data -p 8777 -U \
                     root eucalyptus_vmwarebroker",
                    suggest_filename="eucalyptus_vmwarebroker.sql",
                    timeout=600
                )

        if (
            os.path.isfile('/usr/pgsql-9.1/bin/psql') and
            self.check_postgres()
        ):
            self.collectExtOutput(
                "/usr/pgsql-9.1/bin/psql -h /var/lib/eucalyptus/db/data \
                 -p 8777 -U root -c \"SELECT \
                 pg_database.datname,pg_database_size(pg_database.datname),\
                 pg_size_pretty(pg_database_size(pg_database.datname)) \
                 FROM pg_database ORDER BY pg_database_size DESC;\" \
                 -d database_events",
                suggest_filename="database_sizes.txt",
                timeout=600
            )

        if os.path.isfile('/var/lib/eucalyptus/db/data/pg_hba.conf'):
            self.addCopySpec('/var/lib/eucalyptus/db/data/pg_hba.conf')

        if os.path.isfile('/var/lib/eucalyptus/db/data/pg_hba.conf.org'):
            self.addCopySpec('/var/lib/eucalyptus/db/data/pg_hba.conf.org')

        if os.path.isfile('/var/lib/eucalyptus/db/data/pg_ident.conf'):
            self.addCopySpec('/var/lib/eucalyptus/db/data/pg_ident.conf')

        if os.path.isfile('/var/lib/eucalyptus/db/data/postgresql.conf'):
            self.addCopySpec('/var/lib/eucalyptus/db/data/postgresql.conf')

        if os.path.isfile('/var/lib/eucalyptus/db/data/postgresql.conf.org'):
            self.addCopySpec('/var/lib/eucalyptus/db/data/postgresql.conf.org')

        return
