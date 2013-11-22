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
import os, subprocess
import tempfile
import re

class eucafrontend(sos.plugintools.PluginBase):
    """Eucalyptus Cloud - Frontend
    """
    def checkenabled(self):
        if self.isInstalled("euca2ools") and self.isInstalled("eucalyptus-admin-tools") and self.isInstalled("eucalyptus-cloud"):
            return True
        return False

    def clc_status(self):
        clc_check_cmd = ["/sbin/service", "eucalyptus-cloud", "status"]
        """
        Check for eucalyptus-cloud process 
        """
        try:
            clc_check_output,unused_val = subprocess.Popen(clc_check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        except OSError, e:
            if 'No such' in error_string:
                self.addDiagnose("Error checking eucalyptus-cloud process status")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 

        if re.match("^Eucalyptus services are running", clc_check_output):
            self.addDiagnose("Eucalyptus services are running")
            pass
        else:
            """
            Check for eucalyptus-cloud process (in case error with /sbin/service check) 
            """
            clc_pgrep_cmd = ["/usr/bin/pgrep", "eucalyptus"]
            try:
                clc_pgrep_chk, unused_val = subprocess.Popen(clc_pgrep_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()                
            except OSError, e:
                if 'No such' in error_string:
                    self.addDiagnose("Error checking eucalyptus-cloud process status")
                    raise OSError(e)
                else:
                    self.addDiagnose("Error: %s" % e)
                    raise OSError(e) 
            
            if clc_pgrep_chk:
                for proc in clc_pgrep_chk.splitlines():
                    if not proc:
                        raise
                    else:
                        self.addDiagnose("Eucalyptus services are running: " + proc + ".")
            else:
                self.addDiagnose("Error checking eucalyptus-cloud process status")
                print "### eucalyptus-cloud process doesn't seem to be running"
                raise

    def eucacreds_setup(self):
        """
        Grab admin user of eucalyptus account for euca2ools commands
        """
        try:
            mkdir_output = tempfile.mkdtemp(dir='/tmp')
        except OSError, e:
                self.addDiagnose("Error creating directory under /tmp")
                raise OSError(e)

        getcreds_cmd = ["/usr/sbin/euca-get-credentials", "-a", "eucalyptus", "-u", "admin", mkdir_output + "/admin.zip"]
        unzip_cmd = ["/usr/bin/unzip", mkdir_output + "/admin.zip", "-d", mkdir_output ]
        try:
            getcreds_output = subprocess.Popen(getcreds_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        except OSError, e:
            error_string = '%s' % e
            if 'No such' in error_string:
                self.addDiagnose("Error grabbing eucalyptus/admin creds. Is CLC up?")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 
        try:
            unzip_output = subprocess.Popen(unzip_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        except OSError, e:
            error_string = '%s' % e
            if 'No such' in error_string:
                self.addDiagnose("Error unzipping admin.zip")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 
        return mkdir_output

    def get_access_key(self, tmp_dir):
        """
        Grab AWS_ACCESS_KEY from unzip admin/eucalyptus credentials
        """
        try:
            with open(tmp_dir + "/eucarc") as eucarc_file:
                for line in eucarc_file:
                    if re.search("^export AWS_ACCESS_KEY", line):
                        name, var = line.partition("=")[::2]
                        access_key = var.replace('\'','').strip()
                        return access_key
            if access_key is None:
                self.addDiagnose("Error grabbing AWS_ACCESS_KEY from " + tmp_dir + "/eucarc")
                raise
        except OSError, e:
            error_string = '%s' % e
            if 'No such' in error_string:
                self.addDiagnose("Error opening " + tmp_dir + "/eucarc")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 
 
    def get_secret_key(self, tmp_dir):
        """
        Grab AWS_SECRET_KEY from unzip admin/eucalyptus credentials
        """
        try:
            with open(tmp_dir + "/eucarc") as eucarc_file:
                for line in eucarc_file:
                    if re.search("^export AWS_SECRET_KEY", line):
                        name, var = line.partition("=")[::2]
                        secret_key = var.replace('\'','').strip()
                        return secret_key
            if secret_key is None:
                self.addDiagnose("Error grabbing AWS_SECRET_KEY from " + tmp_dir + "/eucarc")
                raise
        except OSError, e:
            error_string = '%s' % e
            if 'No such' in error_string:
                self.addDiagnose("Error opening " + tmp_dir + "/eucarc")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 
 
    def get_account_id(self, tmp_dir):
        """
        Grab EC2_USER_ID from unzip admin/eucalyptus credentials
        """
        try:
            with open(tmp_dir + "/eucarc") as eucarc_file:
                for line in eucarc_file:
                    if re.search("^export EC2_USER_ID", line):
                        name, var = line.partition("=")[::2]
                        account_id = var.replace('\'','').strip()
                        return account_id
            if account_id is None:
                self.addDiagnose("Error grabbing EC2_USER_ID from " + tmp_dir + "/eucarc")
                raise
        except OSError, e:
            error_string = '%s' % e
            if 'No such' in error_string:
                self.addDiagnose("Error opening " + tmp_dir + "/eucarc")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 

    def get_s3_url(self, tmp_dir):
        """
        Grab S3_URL from unzip admin/eucalyptus credentials
        """
        try:
            with open(tmp_dir + "/eucarc") as eucarc_file:
                for line in eucarc_file:
                    if re.search("^export S3_URL", line):
                        name, var = line.partition("=")[::2]
                        s3_url = var.strip()
                        return s3_url
            if s3_url is None:
                self.addDiagnose("Error grabbing S3_URL from " + tmp_dir + "/eucarc")
                raise
        except OSError, e:
            error_string = '%s' % e
            if 'No such' in error_string:
                self.addDiagnose("Error opening " + tmp_dir + "/eucarc")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 
        
    def get_ec2_url(self, tmp_dir):
        """
        Grab EC2_URL from unzip admin/eucalyptus credentials
        """
        try:
            with open(tmp_dir + "/eucarc") as eucarc_file:
                for line in eucarc_file:
                    if re.search("^export EC2_URL", line):
                        name, var = line.partition("=")[::2]
                        ec2_url = var.strip()
                        return ec2_url
            if ec2_url is None:
                self.addDiagnose("Error grabbing EC2_URL from " + tmp_dir + "/eucarc")
                raise
        except OSError, e:
            error_string = '%s' % e
            if 'No such' in error_string:
                self.addDiagnose("Error opening " + tmp_dir + "/eucarc")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 
        
    def euca2ools_conf_setup(self, tmp_dir):
        """
        Create ini file under /etc/euca2ools/conf.d directory from
        information contained in unzip admin/eucalyptus credentials file (eucarc)
        """
        try:
            mkdir_output = os.mkdir("/etc/euca2ools/conf.d")
        except OSError, e:
            error_string = '%s' % e
            if 'No such' in error_string:
                self.addDiagnose("Error creating /etc/euca2ools/conf.d directory")
                raise OSError(e)
            elif 'File exist' in error_string:
                self.addDiagnose("WARN: %s" % e)
                pass
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 
        access_key = self.get_access_key(tmp_dir)     
        secret_key = self.get_secret_key(tmp_dir)
        account_id = self.get_account_id(tmp_dir)
        s3_url = self.get_s3_url(tmp_dir)
        euca2ools_conf = open('/etc/euca2ools/conf.d/sos-euca2ools.ini', 'w')
        try:
            euca2ools_conf.write("[user admin]\n") 
            euca2ools_conf.write("key-id = " + access_key + "\n")
            euca2ools_conf.write("secret-key = " + secret_key + "\n")
            euca2ools_conf.write("account-id = " + account_id + "\n\n")
            euca2ools_conf.write("[region sosreport]\n")
            euca2ools_conf.write("autoscaling-url = http://127.0.0.1:8773/services/AutoScaling/\n")
            euca2ools_conf.write("ec2-url = http://127.0.0.1:8773/services/Eucalyptus/\n")
            euca2ools_conf.write("elasticloadbalancing-url = http://127.0.0.1:8773/services/LoadBalancing/\n")
            euca2ools_conf.write("iam-url = http://127.0.0.1:8773/services/Euare/\n")
            euca2ools_conf.write("monitoring-url = http://127.0.0.1:8773/services/CloudWatch/\n")
            euca2ools_conf.write("s3-url = " + s3_url + "/" + "\n")
            euca2ools_conf.write("sts-url = http://127.0.0.1:8773/services/Tokens/\n")
            euca2ools_conf.write("eustore-url = http://emis.eucalyptus.com/\n")
            euca2ools_conf.write("configuration-url = http://127.0.0.1:8773/services/Configuration/\n")
            euca2ools_conf.write("empyrean-url = http://127.0.0.1:8773/services/Empyrean/\n")
            euca2ools_conf.write("properties-url = http://127.0.0.1:8773/services/Properties/\n")
            euca2ools_conf.write("reporting-url = http://127.0.0.1:8773/services/Reporting/\n")
            euca2ools_conf.write("certificate = /var/lib/eucalyptus/keys/cloud-cert.pem\n")
        finally:
            euca2ools_conf.close()
            self.addDiagnose("Populated /etc/euca2ools/conf.d/sos-euca2ools.ini with admin creds")

    def get_accountlist(self):
        """
        Grab a listing of Euare accounts and return the list
        """
        get_accountlist_cmd = ["/usr/bin/euare-accountlist", "--region", "admin@sosreport"]
        try:
            getaccountlist_output,unused_val = subprocess.Popen(get_accountlist_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        except OSError, e:
            error_string = '%s' % e
            if 'No such' in error_string:
                self.addDiagnose("Error grabbing Euare Account List.")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 
        accounts =[]
        for account_info in getaccountlist_output.splitlines():
            entry = re.split(r'\t',account_info)
            accounts.append(entry[0])    
        return accounts

    def get_account_info(self, account):
        """
        Grab resources associated with the Euare account passed in
        """
        self.collectExtOutput("/usr/bin/euare-accountaliaslist --as-account " + account + " --region admin@sosreport", suggest_filename="euare-accountaliaslist-" + account)
        self.collectExtOutput("/usr/bin/euare-accountlistpolicies -a " + account + " -v --region admin@sosreport", suggest_filename="euare-accountlistpolicies-" + account)
        self.collectExtOutput("/usr/bin/euare-userlistbypath --as-account " + account + " --region admin@sosreport", suggest_filename="euare-userlistbypath-" + account)
        self.collectExtOutput("/usr/bin/euare-grouplistbypath --as-account " + account + " --region admin@sosreport", suggest_filename="euare-grouplistbypath-" + account)

    def get_userlist(self, account):
        """
        Grab list of users of the Euare account passed in and return the list of users
        """
        get_userlist_cmd = ["/usr/bin/euare-userlistbypath", "--as-account", account, "--region", "admin@sosreport"]
        try:
            getuserlist_output,unused_val = subprocess.Popen(get_userlist_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        except OSError, e:
            error_string = '%s' % e
            if 'No such' in error_string:
                self.addDiagnose("Error grabbing Euare Account " + account + " User List.")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 
        users =[]
        sColon = re.compile('[:]')
        for user_info in getuserlist_output.splitlines():
            entry = sColon.split(user_info)
            user_id = entry[5].strip().split("/")
            users.append(user_id[1])    
        return users

    def get_account_user_info(self, account, user):
        """
        Grab resources of users in the Euare account passed in
        """
        self.collectExtOutput("/usr/bin/euare-usergetinfo --as-account " + account + " -u " + user + " --region admin@sosreport", suggest_filename="euare-usergetinfo-" + account + "-" + user)
        self.collectExtOutput("/usr/bin/euare-usergetloginprofile --as-account " + account + " -u " + user + " --region admin@sosreport", suggest_filename="euare-usergetloginprofile-" + account + "-" + user)
        self.collectExtOutput("/usr/bin/euare-userlistcerts --as-account " + account + " -u " + user + " --region admin@sosreport", suggest_filename="euare-userlistcerts-" + account + "-" + user)
        self.collectExtOutput("/usr/bin/euare-usergetattributes --as-account " + account + " -u " + user + " --show-extra --region admin@sosreport", suggest_filename="euare-usergetattributes-" + account + "-" + user)
        self.collectExtOutput("/usr/bin/euare-userlistgroups --as-account " + account + " -u " + user + " --region admin@sosreport", suggest_filename="euare-userlistgroups-" + account + "-" + user)
        self.collectExtOutput("/usr/bin/euare-userlistkeys --as-account " + account + " -u " + user + " --region admin@sosreport", suggest_filename="euare-userlistkeys-" + account + "-" + user)
        self.collectExtOutput("/usr/bin/euare-userlistpolicies --as-account " + account + " -u " + user + " -v --region admin@sosreport", suggest_filename="euare-userlistpolicies-" + account + "-" + user)
    
    def get_grouplist(self, account):
        """
        Grab the groups from the Euare account passed in and return the list
        """
        get_grouplist_cmd = ["/usr/bin/euare-grouplistbypath", "--as-account", account, "--region", "admin@sosreport"]
        try:
            getgrouplist_output,unused_val = subprocess.Popen(get_grouplist_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        except OSError, e:
            error_string = '%s' % e
            if 'No such' in error_string:
                self.addDiagnose("Error grabbing Euare Account " + account + " Group List.")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 
        groups =[]
        sColon = re.compile('[:]')
        for group_info in getgrouplist_output.splitlines():
            if re.search('iam', group_info):
                entry = sColon.split(group_info)
                group_id = entry[5].strip().split("/")
                groups.append(group_id[1])    
        return groups

    def get_account_group_info(self, account, group):
        """
        Grab the resources of the groups in the Euare account passed in
        """
        self.collectExtOutput("/usr/bin/euare-grouplistusers --as-account " + account + " -g " + group + " --region admin@sosreport", suggest_filename="euare-grouplistusers-" + account + "-" + group)
        self.collectExtOutput("/usr/bin/euare-grouplistpolicies --as-account " + account + " -g " + group + " -v --region admin@sosreport", suggest_filename="euare-grouplistpolicies-" + account + "-" + group)

    def cleanup(self, tmp_dir):
        """
        Clean up temporary directory and sos-euca2ools.ini file.
        """
        self.addDiagnose("### Cleanup credentials ###")
        self.collectExtOutput("rm -rf " + tmp_dir, suggest_filename="cleanup-tmpeucacreds")
        self.collectExtOutput("rm -rf /etc/euca2ools/conf.d/sos-euca2ools.ini", suggest_filename="cleanup-sos-euca2ools-config")
 
    def setup(self):
        self.addDiagnose("### Check to make sure eucalyptus-cloud is running ###")
        self.clc_status()
        self.addDiagnose("### Grabbing eucalyptus/admin credentials ###")
        tmp_dir = self.eucacreds_setup()
        self.addDiagnose("### Setting up sos-euca2ools.ini file ###")
        self.euca2ools_conf_setup(tmp_dir)
        self.addCopySpec("/etc/euca2ools")
        self.addCopySpec("/tmp/eucacreds")
        self.addDiagnose("### Grabbing Cloud Resource Data ###")
        self.collectExtOutput("/usr/bin/euca-describe-addresses verbose --region admin@sosreport", suggest_filename="euca-describe-addresses-verbose")
        self.collectExtOutput("/usr/bin/euca-describe-availability-zones verbose --region admin@sosreport", suggest_filename="euca-describe-availability-zones-verbose")
        self.collectExtOutput("/usr/bin/euca-describe-groups verbose --region admin@sosreport", suggest_filename="euca-describe-groups-verbose")
        self.collectExtOutput("/usr/bin/euca-describe-images --all --region admin@sosreport", suggest_filename="euca-describe-images-all")
        self.collectExtOutput("/usr/bin/eustore-describe-images -v --region admin@sosreport", suggest_filename="eustore-describe-images")
        self.collectExtOutput("/usr/bin/euca-describe-instances verbose --region admin@sosreport", suggest_filename="euca-describe-instances-verbose")
        self.collectExtOutput("/usr/bin/euca-describe-keypairs verbose --region admin@sosreport", suggest_filename="euca-describe-keypairs-verbose")
        self.collectExtOutput("/usr/bin/euca-describe-snapshots verbose --region admin@sosreport", suggest_filename="euca-describe-snapshots-verbose")
        self.collectExtOutput("/usr/bin/euca-describe-volumes verbose --region admin@sosreport", suggest_filename="euca-describe-volumes-verbose")
        self.collectExtOutput("/usr/bin/euca-describe-tags --region admin@sosreport", suggest_filename="euca-describe-tags")
        self.collectExtOutput("/usr/bin/euscale-describe-auto-scaling-instances verbose --show-long --region admin@sosreport", suggest_filename="euscale-describe-auto-scaling-instances-verbose")
        self.collectExtOutput("/usr/bin/euscale-describe-auto-scaling-groups verbose --show-long --region admin@sosreport", suggest_filename="euscale-describe-auto-scaling-groups-verbose")
        self.collectExtOutput("/usr/bin/euscale-describe-launch-configs verbose --show-long --region admin@sosreport", suggest_filename="euscale-describe-launch-configs-verbose")
        self.collectExtOutput("/usr/bin/euscale-describe-notification-configurations verbose --region admin@sosreport", suggest_filename="euscale-describe-notification-configurations-verbose")
        self.collectExtOutput("/usr/bin/euscale-describe-policies verbose --show-long --region admin@sosreport", suggest_filename="euscale-describe-policies-verbose")
        self.collectExtOutput("/usr/bin/euscale-describe-scaling-activities verbose --show-long --region admin@sosreport", suggest_filename="euscale-describe-scaling-activities-verbose")
        self.collectExtOutput("/usr/bin/euscale-describe-scheduled-actions verbose --show-long --region admin@sosreport", suggest_filename="euscale-describe-scheduled-actions-verbose")
        self.collectExtOutput("/usr/bin/eulb-describe-lb-policies verbose --show-long --region admin@sosreport", suggest_filename="eulb-describe-lb-policies-verbose")
        self.collectExtOutput("/usr/bin/eulb-describe-lb-policy-types verbose --show-long --region admin@sosreport", suggest_filename="eulb-describe-lb-policy-types-verbose")
        self.collectExtOutput("/usr/bin/eulb-describe-lbs verbose --show-long --region admin@sosreport", suggest_filename="eulb-describe-lbs-verbose")
        self.collectExtOutput("/usr/bin/euwatch-describe-alarms verbose --show-long --region admin@sosreport", suggest_filename="euwatch-describe-alarms-verbose")
        self.collectExtOutput("/usr/bin/euwatch-describe-alarm-history verbose --show-long --region admin@sosreport", suggest_filename="euwatch-describe-alarm-history-verbose")
        self.collectExtOutput("/usr/bin/euare-accountlist --region admin@sosreport", suggest_filename="euare-accountlist")
        for account in self.get_accountlist():
            self.get_account_info(account)
            for user in self.get_userlist(account):
                self.get_account_user_info(account, user)
            for group in self.get_grouplist(account):
                self.get_account_group_info(account, group)

        self.addDiagnose("### Grabbing Cloud Component Data ###")
        access_key = self.get_access_key(tmp_dir)     
        secret_key = self.get_secret_key(tmp_dir)
        ec2_url = self.get_ec2_url(tmp_dir)
        self.collectExtOutput("/usr/sbin/euca-describe-arbitrators -U " + ec2_url + " -I " + access_key + " -S " + secret_key, suggest_filename="euca-describe-arbitrators")
        self.collectExtOutput("/usr/sbin/euca-describe-clouds -U " + ec2_url + " -I " + access_key + " -S " + secret_key, suggest_filename="euca-describe-clouds")
        self.collectExtOutput("/usr/sbin/euca-describe-clusters -U " + ec2_url + " -I " + access_key + " -S " + secret_key, suggest_filename="euca-describe-clusters")
        self.collectExtOutput("/usr/sbin/euca-describe-components -U " + ec2_url + " -I " + access_key + " -S " + secret_key, suggest_filename="euca-describe-components")
        self.collectExtOutput("/usr/sbin/euca-describe-nodes -U http://127.0.0.1:8773/services/Empyrean/ -I " + access_key + " -S " + secret_key, suggest_filename="euca-describe-nodes")
        self.collectExtOutput("/usr/sbin/euca-describe-properties -U " + ec2_url + " -I " + access_key + " -S " + secret_key, suggest_filename="euca-describe-properties")
        self.collectExtOutput("/usr/bin/euca-describe-regions -U " + ec2_url + " -I " + access_key + " -S " + secret_key, suggest_filename="euca-describe-regions")
        self.collectExtOutput("/usr/sbin/euca-describe-services --all -E", suggest_filename="euca-describe-services-all")
        self.collectExtOutput("/usr/sbin/euca-describe-storage-controllers -U " + ec2_url + " -I " + access_key + " -S " + secret_key, suggest_filename="euca-describe-storage-controllers")
        self.collectExtOutput("/usr/sbin/euca-describe-vmware-brokers -U " + ec2_url + " -I " + access_key + " -S " + secret_key, suggest_filename="euca-describe-vmware-brokers")
        self.collectExtOutput("/usr/sbin/euca-describe-walruses -U " + ec2_url + " -I " + access_key + " -S " + secret_key, suggest_filename="euca-describe-walruses")
        self.collectExtOutput("/usr/bin/euca-version")
        self.cleanup(tmp_dir)
        return

