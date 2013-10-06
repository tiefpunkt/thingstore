from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from datetime import timedelta

from thingstore.models import Thing, Value
from django.contrib.auth.models import User

""" Index page. Contains lists of users and things """
def index(request):
	latest_things = Thing.objects.order_by('name')[:5]
	users = User.objects.order_by('-last_login')[:5]
	context = {'latest_things': latest_things, 'users': users}
	return render(request, 'thingstore/index.html', context)

""" Thing detail page """
def thing(request, thing_id):
	timeframe_hours = 12
	
	# Create Querysets
	thing = get_object_or_404(Thing, pk=thing_id)
	metrics = thing.metrics.all()
	values = Value.objects.filter(metric__in = metrics, timestamp__gte = now()-timedelta(hours=timeframe_hours))
	
	# Put values as dict in a bigger dict
	relation_dict = {}
	for value in values:
		value_dict = value.__dict__
		value_dict['js_time'] = value.js_time
		relation_dict.setdefault(value.metric_id, []).append(value_dict)
	
	# Create dict of metrics, add values from ^ dict
	metrics_list = []
	for metric in metrics:
		metric_dict = metric.__dict__
		metric_dict['current_value'] = metric.current_value
		if metric.id in relation_dict:
			metric_dict['value_dict'] = relation_dict[metric.id]
			
			# add latest invisible value to have a line out of nowhere into the left side of the graph
			invisible_value = Value.objects.filter(metric = metric, timestamp__lt = now()-timedelta(hours=timeframe_hours))[:1]
			if len(invisible_value) == 1:
				value_dict = invisible_value[0].__dict__
				value_dict['js_time'] = invisible_value[0].js_time
				metric_dict['value_dict'].append(value_dict)
		
		metrics_list.append(metric_dict)

	return render(request, 'thingstore/thing.html',
		{
			'thing': thing,
			'metrics': metrics_list,
			'timeframe_hours': timeframe_hours
		}
	)	

""" User detail page """
def user(request, username):
	user = get_object_or_404(User, username__iexact=username)
	return render(request, 'thingstore/user.html', {'user': user})
