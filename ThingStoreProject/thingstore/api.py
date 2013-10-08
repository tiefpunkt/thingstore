from django.conf.urls import patterns, url
from django.http import HttpResponse
from django.views.generic.base import View
from django.shortcuts import get_object_or_404
import json
from django.forms.models import model_to_dict

from thingstore.models import Thing

class APIView(View):
	filetype = "json"
	
	def getJSON(self, request, **kwargs):
		pass
	
	def getCSV(self, request, **kwargs):
		pass
	
	def get(self, request, **kwargs):
		if self.filetype == "json":
			data = self.getJSON(request, **kwargs)
			return HttpResponse(data, content_type="application/json")
		elif self.filetype == "csv":
			data = self.getCSV(request, **kwargs)
			return HttpResponse(data, content_type="text/plain")

class ThingAPI(APIView):
	def getJSON(self, request, **kwargs):
		thing = get_object_or_404(Thing, pk=kwargs["thing_id"])
		print self.filetype
		metrics = thing.metrics.all()
		data = json.dumps(model_to_dict(thing))
		return data
	
	def getCSV(self, request, **kwargs):
		thing = get_object_or_404(Thing, pk=kwargs["thing_id"])
		metrics = thing.metrics.all()
		data = ""
		for metric in metrics:
			data = "%s%s,%s\n" % (data, metric.name, metric.current_value)
		return data
		
def metric(request):
	
	pass
	
urls = patterns('',
	url(r'^thing/(?P<thing_id>\w+).json', ThingAPI.as_view(filetype="json")),
	url(r'^thing/(?P<thing_id>\w+).csv', ThingAPI.as_view(filetype="csv")),
)
