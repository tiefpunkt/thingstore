from django.conf.urls import patterns, url
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.generic.base import View
from django.shortcuts import get_object_or_404
import json
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout

from thingstore.models import Thing, Metric

class APIView(View):
	filetype = "json"

	# Required because of django's csrf protection
	@csrf_exempt
	def dispatch(self, *args, **kwargs):
		return super(APIView, self).dispatch(*args, **kwargs)

	# abstract call when a json is requested
	def getJSON(self, request, **kwargs):
		pass

	# abstract call when a csv is requested
	def getCSV(self, request, **kwargs):
		pass

	# dispatches GET requests depending on requested file type
	def get(self, request, **kwargs):
		if self.filetype == "json":
			data = self.getJSON(request, **kwargs)
			return HttpResponse(data, content_type="application/json")
		elif self.filetype == "csv":
			data = self.getCSV(request, **kwargs)
			return HttpResponse(data, content_type="text/plain")

	# abstract call when a JSON is sent as a PUT request
	def putJSON(self, request, **kwargs):
		pass

	# abstract call when a CSV is sent as a PUT request
	def putCSV(self, request, **kwargs):
		pass

	# dispatches PUT requests
	def put(self, request, **kwargs):

		# API Key authentication
		# Only if not already authenticated by some other means
		used_apikey = False
		if not request.user.is_authenticated():
			try:
				apikey = request.GET['apikey']
				user = authenticate(apikey=apikey)
			except:
				user = None
			if user is not None:
				if user.is_active:
					login(request, user)
					used_apikey = True
				else:
					return HttpResponseForbidden("Your user is disabled.\n", content_type="text/plain")
			else:
				return HttpResponseForbidden("You need to provide a valid API key to access this resource.\n", content_type="text/plain")

		response = None
		if self.filetype == "json":
			response = self.putJson(request, **kwargs)
		elif self.filetype == "csv":
			response = self.putCSV(request, **kwargs)

		# logout if logged in by apikey
		if (used_apikey):
			logout(request)

		return response

# API resource of Things
class ThingAPI(APIView):

	# Return a JSON describing the thing, with current values of the metrics
	def getJSON(self, request, **kwargs):
		thing = get_object_or_404(Thing, pk=kwargs["thing_id"])

		data = model_to_dict(thing)

		data['metrics'] = {}
		metrics = thing.metrics.all()
		for metric in metrics:
			data['metrics'][metric.name] = model_to_dict(metric,fields=['name','unit'])
			data['metrics'][metric.name]['current_value'] = metric.current_value
			data['metrics'][metric.name]['id'] = metric.id
		return json.dumps(data)

	# Return a CSV with current values of all metrics of the thing
	def getCSV(self, request, **kwargs):
		thing = get_object_or_404(Thing, pk=kwargs["thing_id"])
		metrics = thing.metrics.all()
		data = ""
		for metric in metrics:
			data = "%s%s,%s\n" % (data, metric.name, metric.current_value)
		return data

	# Update a thing's metrics. Eventually, at least.
	def putCSV(self, request, **kwargs):
		thing = get_object_or_404(Thing, pk=kwargs["thing_id"])

		if thing.owner != request.user:
			return HttpResponseForbidden("Your user is not allowed to access this thing.\n", content_type="text/plain")

		body = request.body.strip()
		lines = body.split('\n')
		data = []
		for line in lines:
			line_data = line.strip().split(',')
			if len(line_data) != 2:
				return HttpResponseBadRequest("ERROR\n", content_type="text/plain")
			data.append(line_data)

		try:
			self.writeToMetrics(thing, data)
		except Exception as err:
			return  HttpResponseBadRequest(unicode(err) + "\n", content_type="text/plain")

		return HttpResponse(data, content_type="text/plain")

	def writeToMetrics(self, thing, data):
		# Check whether ALL metrics exist, before updating them
		# TODO: pretty DB heavy, might need a better solutions.
		# maybe we can solve this with DB transactions.
		# See https://docs.djangoproject.com/en/dev/topics/db/transactions/
		# Check values as well.
		for metric in data:
			if thing.metrics.filter(name = metric[0]).count() <> 1:
				raise Exception("Metric \"" + metric[0] + "\" does not exist.")

			try:
				float(metric[1])
			except ValueError:
				# Not a numeric value. No likey
				raise Exception("\"" + metric[1] + "\" is not a valid value for metric \"" + metric[0] + "\".")

		for metric in data:
			thing.metrics.get(name=metric[0]).current_value = metric[1]



class MetricAPI(APIView):
	# Return a JSON describing the thing, with current values of the metrics
	def getJSON(self, request, **kwargs):

		# Check if metric_name or metric_id is supplied and try to retrieve metric object
		try:
			metric = get_object_or_404(Metric, name=kwargs["metric_name"], thing=kwargs["thing_id"])
		except KeyError:
			metric = get_object_or_404(Metric, pk=kwargs["metric_id"], thing=kwargs["thing_id"])

		rdata = {}

		rdata['name'] = metric.name
		if metric.current_value is not None:
			rdata['current_value'] = float(metric.current_value)
		else:
			rdata['current_value'] = 0.0
		rdata['id'] = metric.id

		try:
			timeframe = int(request.GET.get('apitimeframe',''))
		except (KeyError, ValueError):
			timeframe = 12; #12h default

		values = metric.getValues(timeframe)

		try:
			rdata['data'] =	[ [value.js_time,value.value] for value in values ]
		except:
			rdata['data'] = [ ]
			rdata['message'] = 'an error occured'

		return json.dumps(rdata)

def metric(request):
	pass

urls = patterns('',
	url(r'^thing/(?P<thing_id>\d+).json', ThingAPI.as_view(filetype="json")),
	url(r'^thing/(?P<thing_id>\d+).csv', ThingAPI.as_view(filetype="csv")),
	url(r'^thing/(?P<thing_id>\d+)/(?P<metric_id>\d+).json', MetricAPI.as_view(filetype="json")),
	url(r'^thing/(?P<thing_id>\d+)/(?P<metric_name>.+).json', MetricAPI.as_view(filetype="json")),
)
