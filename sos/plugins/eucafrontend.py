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

    def checkversion(self, pkg):
        eucapkg = self.policy().pkgByName(pkg)
        return eucapkg.version

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
        Grab EC2_ACCESS_KEY from unzip admin/eucalyptus credentials
        """
        try:
            with open(tmp_dir + "/eucarc") as eucarc_file:
                for line in eucarc_file:
                    if re.search("^export EC2_ACCESS_KEY", line):
                        name, var = line.partition("=")[::2]
                        access_key = var.replace('\'','').strip()
                        return access_key
            if access_key is None:
                self.addDiagnose("Error grabbing EC2_ACCESS_KEY from " + tmp_dir + "/eucarc")
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
        Grab EC2_SECRET_KEY from unzip admin/eucalyptus credentials
        """
        try:
            with open(tmp_dir + "/eucarc") as eucarc_file:
                for line in eucarc_file:
                    if re.search("^export EC2_SECRET_KEY", line):
                        name, var = line.partition("=")[::2]
                        secret_key = var.replace('\'','').strip()
                        return secret_key
            if secret_key is None:
                self.addDiagnose("Error grabbing EC2_SECRET_KEY from " + tmp_dir + "/eucarc")
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
        
    def get_iam_url(self, tmp_dir):
        """
        Grab AWS_IAM_URL/EUARE_URL from unzip admin/eucalyptus credentials
        """
        self.addDiagnose("## Checking euca2ools version to confirm which AWS_IAM_URL/EUARE_URL pattern use")
        euca2ools_version = self.checkversion('euca2ools')
        if re.match('^3.1+', euca2ools_version):
            iam_pattern = "^export AWS_IAM_URL"
        else:
            iam_pattern = "^export EUARE"

        try:
            with open(tmp_dir + "/eucarc") as eucarc_file:
                for line in eucarc_file:
                    if re.search(iam_pattern, line):
                        name, var = line.partition("=")[::2]
                        iam_url = var.strip()
                        return iam_url
            if iam_url is None:
                self.addDiagnose("Error grabbing AWS_IAM_URL/EUARE_URL from " + tmp_dir + "/eucarc")
                raise
        except OSError, e:
            error_string = '%s' % e
            if 'No such' in error_string:
                self.addDiagnose("Error opening " + tmp_dir + "/eucarc")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 
        
    def get_autoscale_url(self, tmp_dir):
        """
        Grab AWS_AUTO_SCALING_URL from unzip admin/eucalyptus credentials
        """
        try:
            with open(tmp_dir + "/eucarc") as eucarc_file:
                for line in eucarc_file:
                    if re.search("^export AWS_AUTO_SCALING", line):
                        name, var = line.partition("=")[::2]
                        autoscale_url = var.strip()
                        return autoscale_url
            if autoscale_url is None:
                self.addDiagnose("Error grabbing AWS_AUTO_SCALING_URL from " + tmp_dir + "/eucarc")
                raise
        except OSError, e:
            error_string = '%s' % e
            if 'No such' in error_string:
                self.addDiagnose("Error opening " + tmp_dir + "/eucarc")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 
        
    def get_elb_url(self, tmp_dir):
        """
        Grab AWS_ELB_URL from unzip admin/eucalyptus credentials
        """
        try:
            with open(tmp_dir + "/eucarc") as eucarc_file:
                for line in eucarc_file:
                    if re.search("^export AWS_ELB", line):
                        name, var = line.partition("=")[::2]
                        elb_url = var.strip()
                        return elb_url
            if elb_url is None:
                self.addDiagnose("Error grabbing AWS_ELB_URL from " + tmp_dir + "/eucarc")
                raise
        except OSError, e:
            error_string = '%s' % e
            if 'No such' in error_string:
                self.addDiagnose("Error opening " + tmp_dir + "/eucarc")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 
        
    def get_cloudwatch_url(self, tmp_dir):
        """
        Grab AWS_CLOUDWATCH_URL from unzip admin/eucalyptus credentials
        """
        try:
            with open(tmp_dir + "/eucarc") as eucarc_file:
                for line in eucarc_file:
                    if re.search("^export AWS_CLOUDWATCH", line):
                        name, var = line.partition("=")[::2]
                        cloudwatch_url = var.strip()
                        return cloudwatch_url
            if cloudwatch_url is None:
                self.addDiagnose("Error grabbing AWS_CLOUDWATCH_URL from " + tmp_dir + "/eucarc")
                raise
        except OSError, e:
            error_string = '%s' % e
            if 'No such' in error_string:
                self.addDiagnose("Error opening " + tmp_dir + "/eucarc")
                raise OSError(e)
            else:
                self.addDiagnose("Error: %s" % e)
                raise OSError(e) 
        
    def get_sts_url(self, tmp_dir):
        """
        Grab TOKEN_URL from unzip admin/eucalyptus credentials
        """
        try:
            with open(tmp_dir + "/eucarc") as eucarc_file:
                for line in eucarc_file:
                    if re.search("^export TOKEN", line):
                        name, var = line.partition("=")[::2]
                        sts_url = var.strip()
                        return sts_url
            if sts_url is None:
                self.addDiagnose("Error grabbing STS_URL from " + tmp_dir + "/eucarc")
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
        ec2_url = self.get_ec2_url(tmp_dir)
        iam_url = self.get_iam_url(tmp_dir)
        autoscale_url = self.get_autoscale_url(tmp_dir)
        elb_url = self.get_elb_url(tmp_dir)
        cloudwatch_url = self.get_cloudwatch_url(tmp_dir)
        sts_url = self.get_sts_url(tmp_dir)
        euca2ools_conf = open('/etc/euca2ools/conf.d/sos-euca2ools.ini', 'w')
        try:
            euca2ools_conf.write("[user admin]\n") 
            euca2ools_conf.write("key-id = " + access_key + "\n")
            euca2ools_conf.write("secret-key = " + secret_key + "\n")
            euca2ools_conf.write("account-id = " + account_id + "\n\n")
            euca2ools_conf.write("[region sosreport]\n")
            euca2ools_conf.write("autoscaling-url = " + autoscale_url + "/" + "\n")
            euca2ools_conf.write("ec2-url = " + ec2_url + "/" + "\n")
            euca2ools_conf.write("elasticloadbalancing-url = " + elb_url + "/" + "\n")
            euca2ools_conf.write("iam-url = " + iam_url + "/" + "\n")
            euca2ools_conf.write("monitoring-url = " + cloudwatch_url + "/" + "\n")
            euca2ools_conf.write("s3-url = " + s3_url + "/" + "\n")
            euca2ools_conf.write("sts-url = " + sts_url + "/" + "\n")
            euca2ools_conf.write("eustore-url = http://emis.eucalyptus.com/\n")
            euca2ools_conf.write("configuration-url = http://127.0.0.1:8773/services/Configuration/\n")
            euca2ools_conf.write("empyrean-url = http://127.0.0.1:8773/services/Empyrean/\n")
            euca2ools_conf.write("properties-url = http://127.0.0.1:8773/services/Properties/\n")
            euca2ools_conf.write("reporting-url = http://127.0.0.1:8773/services/Reporting/\n")
            euca2ools_conf.write("certificate = /var/lib/eucalyptus/keys/cloud-cert.pem\n")
        finally:
            euca2ools_conf.close()
            self.addDiagnose("Populated /etc/euca2ools/conf.d/sos-euca2ools.ini with admin creds")

    def get_accountlist(self, tmp_dir=''):
        """
        Grab a listing of Euare accounts and return the list
        """
        self.addDiagnose("### Grabbing version of euca2ools ###")
        euca2ools_version = self.checkversion('euca2ools')
        if re.match('^2.1+', euca2ools_version) and tmp_dir:
            access_key = self.get_access_key(tmp_dir)     
            secret_key = self.get_secret_key(tmp_dir)
            iam_url = self.get_iam_url(tmp_dir)
            get_accountlist_cmd = ["/usr/bin/euare-accountlist", "-U", iam_url, "-I", access_key, "-S", secret_key]
        else:
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

    def get_account_info(self, account, tmp_dir=''):
        """
        Grab resources associated with the Euare account passed in
        """
        self.addDiagnose("### Grabbing version of euca2ools ###")
        euca2ools_version = self.checkversion('euca2ools')
        if re.match('^2.1+', euca2ools_version) and tmp_dir:
            access_key = self.get_access_key(tmp_dir)     
            secret_key = self.get_secret_key(tmp_dir)
            iam_url = self.get_iam_url(tmp_dir)
            creds_info = " -U " + iam_url + " -I " + access_key + " -S " + secret_key
            self.collectExtOutput("/usr/bin/euare-accountaliaslist --delegate " + account + creds_info, suggest_filename="euare-accountaliaslist-" + account)
            self.collectExtOutput("/usr/bin/euare-accountlistpolicies -a " + account + creds_info, suggest_filename="euare-accountlistpolicies-" + account)
            self.collectExtOutput("/usr/bin/euare-userlistbypath --delegate " + account + creds_info, suggest_filename="euare-userlistbypath-" + account)
            self.collectExtOutput("/usr/bin/euare-grouplistbypath --delegate " + account + creds_info, suggest_filename="euare-grouplistbypath-" + account)
        else:
            self.collectExtOutput("/usr/bin/euare-accountaliaslist --as-account " + account + " --region admin@sosreport", suggest_filename="euare-accountaliaslist-" + account)
            self.collectExtOutput("/usr/bin/euare-accountlistpolicies -a " + account + " -v --region admin@sosreport", suggest_filename="euare-accountlistpolicies-" + account)
            self.collectExtOutput("/usr/bin/euare-userlistbypath --as-account " + account + " --region admin@sosreport", suggest_filename="euare-userlistbypath-" + account)
            self.collectExtOutput("/usr/bin/euare-grouplistbypath --as-account " + account + " --region admin@sosreport", suggest_filename="euare-grouplistbypath-" + account)

    def get_userlist(self, account, tmp_dir=''):
        """
        Grab list of users of the Euare account passed in and return the list of users
        """
        self.addDiagnose("### Grabbing version of euca2ools ###")
        euca2ools_version = self.checkversion('euca2ools')
        if re.match('^2.1+', euca2ools_version) and tmp_dir:
            access_key = self.get_access_key(tmp_dir)     
            secret_key = self.get_secret_key(tmp_dir)
            iam_url = self.get_iam_url(tmp_dir)
            if re.match('^eucalyptus', account):
                get_userlist_cmd = ["/usr/bin/euare-userlistbypath", "-U", iam_url, "-I", access_key, "-S", secret_key]
            else:
                get_userlist_cmd = ["/usr/bin/euare-userlistbypath", "--delegate", account, "-U", iam_url, "-I", access_key, "-S", secret_key]
        else:
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

    def get_account_user_info(self, account, user, tmp_dir=''):
        """
        Grab resources of users in the Euare account passed in
        """
        self.addDiagnose("### Grabbing version of euca2ools ###")
        euca2ools_version = self.checkversion('euca2ools')
        if re.match('^2.1+', euca2ools_version) and tmp_dir:
            access_key = self.get_access_key(tmp_dir)     
            secret_key = self.get_secret_key(tmp_dir)
            iam_url = self.get_iam_url(tmp_dir)
            creds_info = " -U " + iam_url + " -I " + access_key + " -S " + secret_key
            if re.match('^eucalyptus', account):
                delegate = ''
            else:
                delegate = "--delegate " + account
            self.collectExtOutput("/usr/bin/euare-usergetinfo " + delegate + " -u " + user + creds_info, suggest_filename="euare-usergetinfo-" + account + "-" + user)
            self.collectExtOutput("/usr/bin/euare-usergetloginprofile " + delegate + " -u " + user + creds_info, suggest_filename="euare-usergetloginprofile-" + account + "-" + user)
            self.collectExtOutput("/usr/bin/euare-userlistcerts " + delegate + " -u " + user + creds_info, suggest_filename="euare-userlistcerts-" + account + "-" + user)
            self.collectExtOutput("/usr/bin/euare-usergetattributes " + delegate + " -u " + user + " --show-extra" + creds_info, suggest_filename="euare-usergetattributes-" + account + "-" + user)
            self.collectExtOutput("/usr/bin/euare-userlistgroups " + delegate + " -u " + user + creds_info, suggest_filename="euare-userlistgroups-" + account + "-" + user)
            self.collectExtOutput("/usr/bin/euare-userlistkeys " + delegate + " -u " + user + creds_info, suggest_filename="euare-userlistkeys-" + account + "-" + user)
            self.collectExtOutput("/usr/bin/euare-userlistpolicies " + delegate + " -u " + user + " -v" + creds_info, suggest_filename="euare-userlistpolicies-" + account + "-" + user)
        else:
            self.collectExtOutput("/usr/bin/euare-usergetinfo --as-account " + account + " -u " + user + " --region admin@sosreport", suggest_filename="euare-usergetinfo-" + account + "-" + user)
            self.collectExtOutput("/usr/bin/euare-usergetloginprofile --as-account " + account + " -u " + user + " --region admin@sosreport", suggest_filename="euare-usergetloginprofile-" + account + "-" + user)
            self.collectExtOutput("/usr/bin/euare-userlistcerts --as-account " + account + " -u " + user + " --region admin@sosreport", suggest_filename="euare-userlistcerts-" + account + "-" + user)
            self.collectExtOutput("/usr/bin/euare-usergetattributes --as-account " + account + " -u " + user + " --show-extra --region admin@sosreport", suggest_filename="euare-usergetattributes-" + account + "-" + user)
            self.collectExtOutput("/usr/bin/euare-userlistgroups --as-account " + account + " -u " + user + " --region admin@sosreport", suggest_filename="euare-userlistgroups-" + account + "-" + user)
            self.collectExtOutput("/usr/bin/euare-userlistkeys --as-account " + account + " -u " + user + " --region admin@sosreport", suggest_filename="euare-userlistkeys-" + account + "-" + user)
            self.collectExtOutput("/usr/bin/euare-userlistpolicies --as-account " + account + " -u " + user + " -v --region admin@sosreport", suggest_filename="euare-userlistpolicies-" + account + "-" + user)
    
    def get_grouplist(self, account, tmp_dir=''):
        """
        Grab the groups from the Euare account passed in and return the list
        """
        self.addDiagnose("### Grabbing version of euca2ools ###")
        euca2ools_version = self.checkversion('euca2ools')
        if re.match('^2.1+', euca2ools_version) and tmp_dir:
            access_key = self.get_access_key(tmp_dir)     
            secret_key = self.get_secret_key(tmp_dir)
            iam_url = self.get_iam_url(tmp_dir)
            if re.match('^eucalyptus', account):
                get_grouplist_cmd = ["/usr/bin/euare-grouplistbypath", "-U", iam_url, "-I", access_key, "-S", secret_key]
            else:
                get_grouplist_cmd = ["/usr/bin/euare-grouplistbypath", "--delegate", account, "-U", iam_url, "-I", access_key, "-S", secret_key]
        else:
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

    def get_account_group_info(self, account, group, tmp_dir=''):
        """
        Grab the resources of the groups in the Euare account passed in
        """
        self.addDiagnose("### Grabbing version of euca2ools ###")
        euca2ools_version = self.checkversion('euca2ools')
        if re.match('^2.1+', euca2ools_version):
            access_key = self.get_access_key(tmp_dir)     
            secret_key = self.get_secret_key(tmp_dir)
            iam_url = self.get_iam_url(tmp_dir)
            creds_info = " -U " + iam_url + " -I " + access_key + " -S " + secret_key
            if re.match('^eucalyptus', account):
                delegate = ''
            else:
                delegate = "--delegate " + account
            self.collectExtOutput("/usr/bin/euare-grouplistusers " + delegate + " -g " + group + creds_info, suggest_filename="euare-grouplistusers-" + account + "-" + group)
            self.collectExtOutput("/usr/bin/euare-grouplistpolicies " + delegate + " -g " + group + " -v" + creds_info, suggest_filename="euare-grouplistpolicies-" + account + "-" + group)
        else:
            self.collectExtOutput("/usr/bin/euare-grouplistusers --as-account " + account + " -g " + group + " --region admin@sosreport", suggest_filename="euare-grouplistusers-" + account + "-" + group)
            self.collectExtOutput("/usr/bin/euare-grouplistpolicies --as-account " + account + " -g " + group + " -v --region admin@sosreport", suggest_filename="euare-grouplistpolicies-" + account + "-" + group)

    def cleanup(self, tmp_dir):
        """
        Clean up temporary directory and sos-euca2ools.ini file.
        """
        self.addDiagnose("### Cleanup credentials ###")
        self.collectExtOutput("rm -rf " + tmp_dir, suggest_filename="cleanup-tmpeucacreds")
        self.collectExtOutput("rm -rf /etc/euca2ools/conf.d/sos-euca2ools.ini", suggest_filename="cleanup-sos-euca2ools-config")

    def eucalyptus_core(self, tmp_dir):
        self.addDiagnose("### Grabbing eucalyptus/admin credentials ###")
        access_key = self.get_access_key(tmp_dir)     
        secret_key = self.get_secret_key(tmp_dir)
        empyrean_url = "http://127.0.0.1:8773/services/Empyrean/"
        creds_info = " -I " + access_key + " -S " + secret_key
        self.collectExtOutput("/usr/sbin/euca-describe-arbitrators -U " + empyrean_url + creds_info, suggest_filename="euca-describe-arbitrators")
        self.collectExtOutput("/usr/sbin/euca-describe-clouds -U " + empyrean_url + creds_info, suggest_filename="euca-describe-clouds")
        self.collectExtOutput("/usr/sbin/euca-describe-clusters -U " + empyrean_url + creds_info, suggest_filename="euca-describe-clusters")
        self.collectExtOutput("/usr/sbin/euca-describe-components -U " + empyrean_url + creds_info, suggest_filename="euca-describe-components")
        self.collectExtOutput("/usr/sbin/euca-describe-nodes -U " + empyrean_url + creds_info, suggest_filename="euca-describe-nodes")
        self.collectExtOutput("/usr/sbin/euca-describe-properties -U " + empyrean_url + creds_info, suggest_filename="euca-describe-properties")
        self.collectExtOutput("/usr/sbin/euca-describe-services --all -E", suggest_filename="euca-describe-services-all")
        self.collectExtOutput("/usr/sbin/euca-describe-storage-controllers -U " + empyrean_url + creds_info, suggest_filename="euca-describe-storage-controllers")
        if self.isInstalled("eucalyptus-enterprise-vmware-broker"):
            self.collectExtOutput("/usr/sbin/euca-describe-vmware-brokers -U " + empyrean_url + creds_info, suggest_filename="euca-describe-vmware-brokers")
        self.collectExtOutput("/usr/sbin/euca-describe-walruses -U " + empyrean_url + creds_info, suggest_filename="euca-describe-walruses")
        self.collectExtOutput("/usr/bin/euca-version")
    
    def eucalyptus_ec2(self, tmp_dir):
        self.addDiagnose("### Grabbing version of euca2ools ###")
        euca2ools_version = self.checkversion('euca2ools')
        if re.match('^2.1+', euca2ools_version):
            access_key = self.get_access_key(tmp_dir)     
            secret_key = self.get_secret_key(tmp_dir)
            ec2_url = self.get_ec2_url(tmp_dir)
            creds_info = "-U " + ec2_url + " --access-key " + access_key + " --secret-key " + secret_key
            self.collectExtOutput("/usr/bin/euca-describe-addresses verbose " + creds_info, suggest_filename="euca-describe-addresses-verbose")
            self.collectExtOutput("/usr/bin/euca-describe-regions " + creds_info, suggest_filename="euca-describe-regions")
            self.collectExtOutput("/usr/bin/euca-describe-availability-zones verbose " + creds_info, suggest_filename="euca-describe-availability-zones-verbose")
            self.collectExtOutput("/usr/bin/euca-describe-instance-types --show-capacity --by-zone " + creds_info, suggest_filename="euca-describe-instance-types-show-capacity")
            self.collectExtOutput("/usr/bin/euca-describe-groups verbose " + creds_info, suggest_filename="euca-describe-groups-verbose")
            self.collectExtOutput("/usr/bin/euca-describe-images --all " + creds_info, suggest_filename="euca-describe-images-all")
            self.collectExtOutput("/usr/bin/eustore-describe-images -v " + creds_info, suggest_filename="eustore-describe-images")
            self.collectExtOutput("/usr/bin/euca-describe-instances verbose " + creds_info, suggest_filename="euca-describe-instances-verbose")
            self.collectExtOutput("/usr/bin/euca-describe-keypairs verbose " + creds_info, suggest_filename="euca-describe-keypairs-verbose")
            self.collectExtOutput("/usr/bin/euca-describe-snapshots verbose " + creds_info, suggest_filename="euca-describe-snapshots-verbose")
            self.collectExtOutput("/usr/bin/euca-describe-volumes verbose " + creds_info, suggest_filename="euca-describe-volumes-verbose")
        else:
            if not os.path.isfile('/etc/euca2ools/conf.d/sos-euca2ools.ini'):
                self.addDiagnose("### Setting up sos-euca2ools.ini file ###")
                self.euca2ools_conf_setup(tmp_dir)
                self.addCopySpec("/etc/euca2ools")
                self.addCopySpec("/tmp/eucacreds")

            self.addDiagnose("### Grabbing Cloud Resource Data ###")
            self.collectExtOutput("/usr/bin/euca-describe-addresses verbose --region admin@sosreport", suggest_filename="euca-describe-addresses-verbose")
            self.collectExtOutput("/usr/bin/euca-describe-availability-zones verbose --region admin@sosreport", suggest_filename="euca-describe-availability-zones-verbose")
            self.collectExtOutput("/usr/bin/euca-describe-instance-types --show-capacity --region admin@sosreport", suggest_filename="euca-describe-instance-types-show-capacity")
            self.collectExtOutput("/usr/bin/euca-describe-groups verbose --region admin@sosreport", suggest_filename="euca-describe-groups-verbose")
            self.collectExtOutput("/usr/bin/euca-describe-images --all --region admin@sosreport", suggest_filename="euca-describe-images-all")
            self.collectExtOutput("/usr/bin/eustore-describe-images -v --region admin@sosreport", suggest_filename="eustore-describe-images")
            self.collectExtOutput("/usr/bin/euca-describe-regions --region admin@sosreport", suggest_filename="euca-describe-regions")
            self.collectExtOutput("/usr/bin/euca-describe-instances verbose --region admin@sosreport", suggest_filename="euca-describe-instances-verbose")
            self.collectExtOutput("/usr/bin/euca-describe-keypairs verbose --region admin@sosreport", suggest_filename="euca-describe-keypairs-verbose")
            self.collectExtOutput("/usr/bin/euca-describe-snapshots verbose --region admin@sosreport", suggest_filename="euca-describe-snapshots-verbose")
            self.collectExtOutput("/usr/bin/euca-describe-volumes verbose --region admin@sosreport", suggest_filename="euca-describe-volumes-verbose")
            self.collectExtOutput("/usr/bin/euca-describe-tags --region admin@sosreport", suggest_filename="euca-describe-tags")

    def eucalyptus_iam(self, tmp_dir):
        self.addDiagnose("### Grabbing version of euca2ools ###")
        euca2ools_version = self.checkversion('euca2ools')
        if re.match('^2.1+', euca2ools_version):
            access_key = self.get_access_key(tmp_dir)     
            secret_key = self.get_secret_key(tmp_dir)
            iam_url = self.get_iam_url(tmp_dir)
            self.collectExtOutput("/usr/bin/euare-accountlist -U " + iam_url + " -I " + access_key + " -S " + secret_key, suggest_filename="euare-accountlist")
            for account in self.get_accountlist(tmp_dir):
                self.get_account_info(account, tmp_dir)
                for user in self.get_userlist(account, tmp_dir):
                    self.get_account_user_info(account, user, tmp_dir)
                for group in self.get_grouplist(account, tmp_dir):
                    self.get_account_group_info(account, group, tmp_dir)
        else:
            if not os.path.isfile('/etc/euca2ools/conf.d/sos-euca2ools.ini'):
                self.addDiagnose("### Setting up sos-euca2ools.ini file ###")
                self.euca2ools_conf_setup(tmp_dir)
                self.addCopySpec("/etc/euca2ools")
                self.addCopySpec("/tmp/eucacreds")

            self.collectExtOutput("/usr/bin/euare-accountlist --region admin@sosreport", suggest_filename="euare-accountlist")
            for account in self.get_accountlist():
                self.get_account_info(account)
                for user in self.get_userlist(account):
                    self.get_account_user_info(account, user)
                for group in self.get_grouplist(account):
                    self.get_account_group_info(account, group)

    def eucalyptus_autoscaling(self):
        self.collectExtOutput("/usr/bin/euscale-describe-auto-scaling-instances verbose --show-long --region admin@sosreport", suggest_filename="euscale-describe-auto-scaling-instances-verbose")
        self.collectExtOutput("/usr/bin/euscale-describe-auto-scaling-groups verbose --show-long --region admin@sosreport", suggest_filename="euscale-describe-auto-scaling-groups-verbose")
        self.collectExtOutput("/usr/bin/euscale-describe-launch-configs verbose --show-long --region admin@sosreport", suggest_filename="euscale-describe-launch-configs-verbose")
        self.collectExtOutput("/usr/bin/euscale-describe-notification-configurations verbose --region admin@sosreport", suggest_filename="euscale-describe-notification-configurations-verbose")
        self.collectExtOutput("/usr/bin/euscale-describe-policies verbose --show-long --region admin@sosreport", suggest_filename="euscale-describe-policies-verbose")
        self.collectExtOutput("/usr/bin/euscale-describe-scaling-activities verbose --show-long --region admin@sosreport", suggest_filename="euscale-describe-scaling-activities-verbose")
        self.collectExtOutput("/usr/bin/euscale-describe-scheduled-actions verbose --show-long --region admin@sosreport", suggest_filename="euscale-describe-scheduled-actions-verbose")

    def eucalyptus_elb(self):
        self.collectExtOutput("/usr/bin/eulb-describe-lb-policies verbose --show-long --region admin@sosreport", suggest_filename="eulb-describe-lb-policies-verbose")
        self.collectExtOutput("/usr/bin/eulb-describe-lb-policy-types verbose --show-long --region admin@sosreport", suggest_filename="eulb-describe-lb-policy-types-verbose")
        self.collectExtOutput("/usr/bin/eulb-describe-lbs verbose --show-long --region admin@sosreport", suggest_filename="eulb-describe-lbs-verbose")
        return

    def eucalyptus_cloudwatch(self):
        self.collectExtOutput("/usr/bin/euwatch-describe-alarms verbose --show-long --region admin@sosreport", suggest_filename="euwatch-describe-alarms-verbose")
        self.collectExtOutput("/usr/bin/euwatch-describe-alarm-history verbose --show-long --region admin@sosreport", suggest_filename="euwatch-describe-alarm-history-verbose")

    def setup(self):
        self.addDiagnose("### Check to make sure eucalyptus-cloud is running ###")
        self.clc_status()
        self.addDiagnose("### Grabbing eucalyptus/admin credentials ###")
        tmp_dir = self.eucacreds_setup()
        self.addDiagnose("### Grab Eucalyptus Core Service Information ###")
        self.eucalyptus_core(tmp_dir)
        self.addDiagnose("### Grab Eucalyptus EC2 Service Information ###")
        self.eucalyptus_ec2(tmp_dir)
        self.addDiagnose("### Grab Eucalyptus IAM Service Information ###")
        self.eucalyptus_iam(tmp_dir)
        euca2ools_version = self.checkversion('euca2ools')
        if re.match('^3+', euca2ools_version):
            self.addDiagnose("### Grab Eucalyptus AutoScaling Service Information ###")
            self.eucalyptus_autoscaling()
            self.addDiagnose("### Grab Eucalyptus Elastic Load Balancing Service Information ###")
            self.eucalyptus_elb()
            self.addDiagnose("### Grab Eucalyptus CloudWatch Service Information ###")
            self.eucalyptus_cloudwatch()
       
        self.cleanup(tmp_dir) 
        return

