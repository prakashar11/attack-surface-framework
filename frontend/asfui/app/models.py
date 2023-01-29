# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User
from os import path
import sys
import os
import re

# Create your models here.

class vdTarget(models.Model):
    name = models.CharField(max_length=150, unique=True)
    author = models.CharField(max_length=100, default='Me')
    lastdate = models.DateTimeField(auto_now=True)
    itemcount = models.IntegerField(default=0)
    asset_type = models.CharField(max_length=100, default='DOMAIN')
    tag = models.CharField(max_length=250, default='DEFAULT')
    owner = models.CharField(max_length=512, default='')
    metadata = models.TextField(default="")
    assetcriticality = models.CharField(max_length=50, default='medium') # critical, high, medium, low
    internetexposed = models.CharField(max_length=50, default='False') # how to determine? TODO may be when wazuh is integrated
    criticalfindings = models.IntegerField(default=0) # with exploits
    highfindings = models.IntegerField(default=0) # with exploits
    info = models.TextField(default="") # store the nmap scan or other freeform text
    
    def __str__(self):
        return self.name.lower()

class vdInTarget(models.Model):
    name = models.CharField(max_length=150, unique=True)
    author = models.CharField(max_length=100, default='Me')
    lastdate = models.DateTimeField(auto_now=True)
    itemcount = models.IntegerField(default=0)
    asset_type = models.CharField(max_length=100, default='DOMAIN')
    tag = models.CharField(max_length=250, default='DEFAULT')
    owner = models.CharField(max_length=512, default='')
    metadata = models.TextField(default="")
    assetcriticality = models.CharField(max_length=50, default='medium') # critical, high, medium, low
    internetexposed = models.CharField(max_length=50, default='False') # how to determine? TODO may be when wazuh is integrated
    criticalfindings = models.IntegerField(default=0) # with exploits
    highfindings = models.IntegerField(default=0) # with exploits
    info = models.TextField(default="") # store the nmap scan or other freeform text 
    
    def __str__(self):
        return self.name.lower()

class vdResult(models.Model):
    # name = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=150)
    asset_type = models.CharField(max_length=30, default="DOMAIN")
    source = models.CharField(max_length=60, default="")
    ipv4 = models.CharField(max_length=20, default="")
    ipv6 = models.CharField(max_length=150, default="")
    lastdate = models.DateTimeField(auto_now=True)
    itemcount = models.IntegerField(default=0)
    tag = models.CharField(max_length=250, default="DEFAULT")
    info = models.CharField(max_length=512, default="")
    owner = models.CharField(max_length=512, default='')
    metadata = models.TextField(max_length=512, default="")
    engine = models.CharField(max_length=50, default="network")
    active = models.CharField(max_length=20, default="No")
    url = models.CharField(max_length=150, default="")
    
    def __str__(self):
        return self.name.lower()
    
    def getList(self):
        return {'name':self.name, 'asset_type':self.asset_type, 'source':self.source, 'ipv4': self.ipv4, 'ipv6':self.ipv6, 'lastdate':str(self.lastdate), 'itemcount':self.itemcount, 'tag':self.tag, 'info':self.info}
    
class vdNucleiResult(models.Model):
    name = models.CharField(max_length=150)
    #True or False Positive -1 -> unset, 0 -> False positive -> True positive
    tfp = models.IntegerField(default=-1)
    asset_type = models.CharField(max_length=30, default="DOMAIN")
    source = models.CharField(max_length=60, default="")
    ipv4 = models.CharField(max_length=20, default="")
    ipv6 = models.CharField(max_length=150, default="")
    lastdate = models.DateTimeField(auto_now=True)
    firstdate = models.DateTimeField(blank=True)
    bumpdate = models.DateTimeField(blank=True)
    port = models.IntegerField(default=0)
    protocol = models.CharField(max_length=40, default="tcp")
    #Nuclei Specific
    detectiondate = models.DateTimeField(blank=True)
    vulnerability = models.CharField(max_length=128)
    ptime = models.CharField(max_length=4, default='P1E')
    #Scope E=External I=Internal
    scope = models.CharField(max_length=1, default='E')
    engine = models.CharField(max_length=50, default="network")
    level = models.CharField(max_length=20, default="critical")
    # status open, closed, hold
    status = models.CharField(max_length=20, default="open")
    # test id that would uniquely identify the alert/result TODO: rename this model to alertResult
    alert_test_id = models.CharField(max_length=512, default="")
    alert_sub_test_id = models.CharField(max_length=512, default="")
    uri = models.CharField(max_length=250)
    full_uri = models.TextField()
    uriistruncated = models.IntegerField(default=0)
    nname = models.CharField(max_length=150, default="unknown")
    #Other
    itemcount = models.IntegerField(default=0)
    tag = models.CharField(max_length=250, default="DEFAULT")
    info = models.TextField(max_length=512, default="")
    owner = models.CharField(max_length=512, default='')
    metadata = models.TextField(default="")
    class Meta:
        unique_together = ('name', 'alert_test_id', 'alert_sub_test_id', 'engine')
    
    def __str__(self):
        return self.name.lower()
    
    def getList(self):
        return {'name':self.name, 'asset_type':self.asset_type, 'source':self.source, 'ipv4': self.ipv4, 'ipv6':self.ipv6, 'lastdate':str(self.lastdate), 'itemcount':self.itemcount, 'tag':self.tag, 'info':self.info}
    
class vdServices(models.Model):
    name = models.CharField(max_length=150, unique=True)
    nname = models.CharField(max_length=150, default="unknown")
    asset_type = models.CharField(max_length=30, default="DOMAIN")
    source = models.CharField(max_length=60, default="")
    ipv4 = models.CharField(max_length=20, default="")
    ipv6 = models.CharField(max_length=150, default="")
    lastdate = models.DateTimeField(auto_now=True)
    itemcount = models.IntegerField(default=0)
    tag = models.CharField(max_length=250, default="")
    ports = models.CharField(max_length=250, default="")
    full_ports = models.TextField(default="")
    service_ssh = models.CharField(max_length=250, default="")
    service_rdp = models.CharField(max_length=250, default="")
    service_telnet = models.CharField(max_length=250, default="")
    service_ftp = models.CharField(max_length=250, default="")
    service_smb = models.CharField(max_length=250, default="")
    nuclei_http = models.TextField(default="")
    info = models.TextField(default="")
    info_gnmap = models.TextField(default="")
    nse_vsanrce = models.CharField(max_length=250, default="")
    owner = models.CharField(max_length=512, default='')
    metadata = models.TextField(default="")
    
    def __str__(self):
        return self.name.lower()

class vdInServices(models.Model):
    name = models.CharField(max_length=150, unique=True)
    nname = models.CharField(max_length=150, default="unknown")
    asset_type = models.CharField(max_length=30, default="DOMAIN")
    source = models.CharField(max_length=60, default="")
    ipv4 = models.CharField(max_length=20, default="")
    ipv6 = models.CharField(max_length=150, default="")
    lastdate = models.DateTimeField(auto_now=True)
    itemcount = models.IntegerField(default=0)
    tag = models.CharField(max_length=250, default="")
    ports = models.CharField(max_length=250, default="")
    full_ports = models.TextField(default="")
    service_ssh = models.CharField(max_length=250, default="")
    service_rdp = models.CharField(max_length=250, default="")
    service_telnet = models.CharField(max_length=250, default="")
    service_ftp = models.CharField(max_length=250, default="")
    service_smb = models.CharField(max_length=250, default="")
    nuclei_http = models.TextField(default="")
    info = models.TextField(default="")
    info_gnmap = models.TextField(default="")
    nse_vsanrce = models.CharField(max_length=250, default="")
    owner = models.CharField(max_length=512, default='')
    metadata = models.TextField(default="")

    
    def __str__(self):
        return self.name.lower()
    
class vdRegExp(models.Model):
    name = models.CharField(max_length=150, unique=True)
    regexp = models.CharField(max_length=250, default=".*")
    exclude = models.CharField(max_length=250, default="")
    tag = models.CharField(max_length=250, default="")
    info = models.TextField(default="")
    def __str__(self):
        return self.name.lower()

class vdJob(models.Model):
    name = models.CharField(max_length=150, unique=True)
    input = models.CharField(max_length=64, default="amass")
    regexp = models.CharField(max_length=250, default="")
    exclude = models.CharField(max_length=250, default="")
    module = models.CharField(max_length=250, default="error")
    tag = models.CharField(max_length=250, default="")
    info = models.TextField(default="")
    def __str__(self):
        return self.name.lower()

class vdNucleiTemplate(models.Model):
    name = models.CharField(max_length=250, default="")
    template_id =  models.CharField(max_length=150, default="")
    severity = models.CharField(max_length=32, default="")
    template = models.CharField(max_length=250, default="")
    enabled = models.CharField(max_length=10, default="No")
    info = models.TextField(max_length=2048, default="")
    def __str__(self):
        return self.name.lower()