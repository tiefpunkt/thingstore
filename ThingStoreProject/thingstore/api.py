from django.conf.urls import url
from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.utils.urls import trailing_slash
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest

from thingstore.models import Thing, Metric, Value

class BaseResource(ModelResource):

	# Remove 'meta' part from the response
	def alter_list_data_to_serialize(self, request, data_dict):
		if isinstance(data_dict, dict):
			if 'meta' in data_dict:
				# Get rid of the "meta".
				del(data_dict['meta'])

		return data_dict

class ThingResource(BaseResource):
	metrics = fields.ToManyField('thingstore.api.MetricResource', 'metrics', full=True)
	
	class Meta:
		queryset = Thing.objects.all()
		authorization = Authorization()
		
""" 
	Nested resources, similar to xively api. doesn't work yet, so let's ignore that
	http://www.maykinmedia.nl/blog/2012/oct/2/nested-resources-tastypie/

	def prepend_urls(self):
		return [
			url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/metrics%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_metric'), name="api_get_metrics"),
		]

	def dispatch_metric(self, request, **kwargs):
		return MetricResource().dispatch('list', request, **kwargs)
"""

class MetricResource(BaseResource):
	current_value = fields.FloatField(attribute='current_value', blank = True, null = True)
	last_update = fields.DateTimeField(attribute='last_update', blank = True, null = True, readonly = True)
	
	class Meta:
		queryset = Metric.objects.all()
		excludes = ['id']
		authorization = Authorization()
		
		"""detail_uri_name = 'name'"""

class ValueResource(BaseResource):
	class Meta:
		queryset = Value.objects.all()
		excludes = ['id']
		authorization = Authorization()
		include_resource_uri = False
		filtering = {
			'timestamp': ['exact', 'range', 'lt', 'lte', 'gte', 'gt'],
			}
        
	def build_filters(self, filters=None):
		if 'metric' not in filters:
			raise BadRequest("missing metric param") # or maybe create your own exception
		return super(ValueResource, self).build_filters(filters)
	
	def alter_list_data_to_serialize(self, request, data_dict):
		if isinstance(data_dict, dict):
			if 'objects' in data_dict:
				# Get rid of the "meta".
				return data_dict['objects']

		return data_dict
