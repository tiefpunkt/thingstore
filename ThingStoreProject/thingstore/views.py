from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from datetime import timedelta

from thingstore.models import Thing, Value
from django.contrib.auth.models import User

def index(request):
	latest_things = Thing.objects.order_by('name')[:5]
	users = User.objects.order_by('-last_login')[:5]
	context = {'latest_things': latest_things, 'users': users}
	return render(request, 'thingstore/index.html', context)
	
def thing(request, thing_id):
	timeframe_hours = 12
	
	thing = get_object_or_404(Thing, pk=thing_id)
	metrics = thing.metrics.all()
	values = Value.objects.filter(metric__in = metrics, timestamp__gt = now()-timedelta(hours=timeframe_hours))
	
	relation_dict = {}
	for value in values:
		value_dict = value.__dict__
		value_dict['js_time'] = value.js_time
		relation_dict.setdefault(value.metric_id, []).append(value_dict)
	
	metrics_list = []
	for metric in metrics:
		metric_dict = metric.__dict__
		metric_dict['current_value'] = metric.current_value
		metric_dict['value_dict'] = relation_dict[metric.id]
		metrics_list.append(metric_dict)

	print metrics_list
	
	return render(request, 'thingstore/thing.html',
		{
			'thing': thing,
			'metrics': metrics_list,
			'timeframe_hours': timeframe_hours
		}
	)	

def user(request, username):
	user = get_object_or_404(User, username__iexact=username)
	return render(request, 'thingstore/user.html', {'user': user})
