from main import models
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse
import all_tags.Moldabek.all_tags
from django.db.models import Q


@login_required(login_url='/admin/')
def index(request):
    with open('json_data/main.json') as json_file:
        params = json.load(json_file)

    return render(request, "report.html", params)


def update_VMB_tags(request):
    all_tags.Moldabek.all_tags.update()
    return HttpResponse("OK")