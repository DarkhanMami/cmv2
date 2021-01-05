from main import models
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse
import os
import all_tags.UAZ_TM.all_tags
import all_tags.Kainar_KUUN.all_tags


@login_required(login_url='/admin/')
def index(request):
    with open('json_data/main.json') as json_file:
        params = json.load(json_file)

    return render(request, "report.html", params)


def update_VMB_tags(request):
    os.system('python /webapps/cmv2/all_tags/Moldabek/all_tags.py')
    return HttpResponse("OK")


def update_Prorva_tags(request):
    os.system('python /webapps/cmv2/all_tags/Prorva/ATB/all_tags.py')
    os.system('python /webapps/cmv2/all_tags/Prorva/CPPN/all_tags.py')
    os.system('python /webapps/cmv2/all_tags/Prorva/DMB/all_tags.py')
    os.system('python /webapps/cmv2/all_tags/Prorva/NRG/all_tags.py')
    os.system('python /webapps/cmv2/all_tags/Prorva/UPPV/all_tags.py')
    os.system('python /webapps/cmv2/all_tags/Prorva/ZPV/all_tags.py')
    return HttpResponse("OK")


def update_Kainar_KUUN_tags(request):
    all_tags.Kainar_KUUN.all_tags.update_tags()
    return HttpResponse("OK")


def update_UAZ_TM_tags(request):
    all_tags.UAZ_TM.all_tags.update_tags()
    return HttpResponse("OK")


def update_UAZ_DRP_tags(request):
    os.system('ipython /webapps/cmv2/all_tags/UAZ_DRP/all_tags.py')
    return HttpResponse("OK")
