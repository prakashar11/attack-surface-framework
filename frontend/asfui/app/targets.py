#!/usr/bin/python3
#Target Abstractions, to avoid copy paste on functions
#from app.tools import debug, PARSER_DEBUG, autodetectType
from datetime import date, datetime
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
import sys
import json
import os.path
import subprocess
import os
from app.nuclei import *
from app.tools import *

def target_new_model(vdTargetModel,vdServicesModel,request,context,autodetectType,delta):
    if 'target_domain' in request.POST:
        domain = request.POST['target_domain'].strip()
        Tag = "NOTFOUND"
        tz = timezone.get_current_timezone()
        LastDate = datetime.now().replace(tzinfo=tz)
        WorkMode = "merge"
        asset_criticality = "medium"
        if "assetcriticality" in request.POST:
            asset_criticality = request.POST['assetcriticality'].strip() 
        if "tag" in request.POST:
            Tag = request.POST['tag'].strip()                
        if not domain == "":
            Type = autodetectType(domain)
            metadata = {}
            metadata['owner']="Admin from UI"
            Jmetadata = json.dumps(metadata)
            vdTargetModel.objects.update_or_create(name=domain, defaults={'asset_type': Type, 'tag':Tag, 'lastdate': LastDate, 'owner': metadata['owner'], 'metadata': Jmetadata}, assetcriticality=asset_criticality)
        if 'target_file' in request.FILES:
            target_file = request.FILES['target_file']
            fs = FileSystemStorage()
            filename = fs.save(target_file.name, target_file)
            uploaded_file_url = fs.url(filename)
            context['target_file'] = uploaded_file_url
            addDomFiles = open(filename, "r")
            for domain in addDomFiles:
                domain = domain.strip()
                Type = autodetectType(domain)
                metadata = {}
                metadata['owner']="Admin from UI"
                metadata['bulk']=target_file.name
                Jmetadata = json.dumps(metadata)
                try:
                    vdTargetModel.objects.update_or_create(name=domain, defaults={'asset_type': Type, 'tag':Tag, 'lastdate': LastDate, 'owner':metadata['owner'], 'metadata': Jmetadata}, assetcriticality=asset_criticality)
                except:
                    sys.stderr.write("Duplicated Target, Skipping:"+domain)
                    
        if 'mode' in request.POST:
            WorkMode = request.POST['mode'].strip()
            sys.stderr.write("WorkMode:"+WorkMode+"\n")
            if WorkMode != 'merge':
                if WorkMode == 'sync':
                    DeleteTarget = vdTargetModel.objects.filter(tag=Tag).filter(lastdate__lt=LastDate)
                if WorkMode == 'delete':
                    #The equals command in filter, does not work for datetimes, so we use __gte instead
                    DeleteTarget = vdTargetModel.objects.filter(tag=Tag).filter(lastdate__gte=LastDate)
                if WorkMode == 'deletebytag':
                    DeleteTarget = vdTargetModel.objects.filter(tag=Tag)
                internal_delete(vdTargetModel,vdServicesModel,DeleteTarget,autodetectType,delta)
                
def target_delete_model(vdTargetModel,vdServicesModel,request,context,autodetectType,delta):
    if 'id' in request.POST:
        id=request.POST['id']
        DeleteTarget = vdTargetModel.objects.filter(id=id)
        internal_delete(vdTargetModel,vdServicesModel,DeleteTarget,autodetectType,delta)
        #DeleteTarget.delete()

def internal_delete(vdTargetModel,vdServicesModel,DeleteTarget,autodetectType,delta):
    for obj in DeleteTarget:
        sys.stderr.write("Obj:"+str(obj)+"\n")
        #Here we really do the work, this will be hard to do, if there are many objects for deletion
        sys.stderr.write("\tSearching:"+str(obj)+" for service deletion\n")
        Name = obj.name
        DeleteFinding = vdServicesModel.objects.filter(name=Name)
        for finding in DeleteFinding:
            sys.stderr.write("\t\tLinked for deletion Obj:"+str(finding)+"\n")
            MSG = get_metadata_array(finding.metadata)
            MSG['owner'] = finding.owner
            MSG['message'] = "[DELETE][OBJECT FROM "+vdTargetModel._meta.object_name+" SERVICES DATABASE]"
            MSG['type'] = autodetectType(finding.name)
            MSG['name'] = finding.name
            MSG['lastupdate'] = str(finding.lastdate)
            delta(MSG)
        #Bulk deletion, no loop required
        DeleteFinding.delete()                    
        DeleteFinding = vdServicesModel.objects.filter(nname=Name)
        for finding in DeleteFinding:
            sys.stderr.write("\t\tLinked for deletion Obj:"+str(finding)+"\n")
            MSG = get_metadata_array(finding.metadata)
            MSG['owner'] = finding.owner
            MSG['message'] = "[DELETE][OBJECT FROM "+vdServicesModel._meta.object_name+" SERVICES DATABASE]"
            MSG['type'] = autodetectType(finding.name)
            MSG['name'] = finding.name
            MSG['lastupdate'] = str(finding.lastdate)
            delta(MSG)
        #Bulk deletion, no loop required
        DeleteFinding.delete()
        MSG = get_metadata_array(obj.metadata)
        #MSG['metadata'] = obj.metadata
        MSG['owner'] = obj.owner
        MSG['message'] = "[DELETE][OBJECT FROM "+vdTargetModel._meta.object_name+" TARGET DATABASE]"
        MSG['type'] = autodetectType(obj.name)
        MSG['name'] = obj.name
        MSG['lastupdate'] = str(obj.lastdate)
        delta(MSG)
        #At this point we delete also nuclei findings, related to domain deletion.
        nuclei_delete_model(MSG)

    DeleteTarget.delete()
