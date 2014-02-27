from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, render_to_response
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from thingstore.models import Thing, Value, APIKey


""" Index page. Contains lists of users and things """
def index(request):
	latest_things = Thing.objects.order_by('name')[:5]
	users = User.objects.order_by('-last_login')[:5]
	context = {'latest_things': latest_things, 'users': users}
	return render(request, 'thingstore/index.html', context)

""" About page. Static """
def about(request):
	context = {}
	return render(request, 'thingstore/about.html', context)

""" Thing detail page """
def thing(request, thing_id):
	timeframe_hours = 1
	
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
	return render(request, 'thingstore/user.html', {'selected_user': user})
	
def login_view(request):
	#state = "Please log in below..."
	username = password = ''
	parameters = {}
	parameters.update(csrf(request))
	
	if request.POST:
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(reverse('thingstore.views.index'))
			else:
				parameters['alert'] = "Your account is not active, please contact the site admin."
		else:
			parameters['alert'] = "Your username and/or password were incorrect."
	

	parameters['username'] = username
	
	return render_to_response('thingstore/login.html',parameters)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('thingstore.views.index'))

@login_required
def settings_personal(request):
	parameters = {}
	if request.POST:
		password = request.POST.get('password')
		password_retype = request.POST.get('password_retype')
		if password <> password_retype:
			parameters["error"] = "Please type the same password twice."

	parameters["tab"] = "personal"
	parameters["apikeys"] = request.user.apikeys.all()
	return render(request, 'thingstore/settings_personal.html', parameters)	

@login_required
def settings_apikeys(request):
	parameters = {}
	parameters["tab"] = "apikeys"
	parameters["apikeys"] = request.user.apikeys.all()
	return render(request, 'thingstore/settings_apikeys.html', parameters)

@login_required
def settings_apikeys_add(request):
		apikey = APIKey.create(request.user)
		apikey.save()
		return HttpResponseRedirect(reverse('thingstore.views.settings_apikeys'))

@login_required
def settings_apikeys_del(request, apikey_id):
		apikey = APIKey.objects.get(pk=apikey_id)
		if apikey.user != request.user:
			return HttpResponseRedirect(reverse('thingstore.views.settings_apikeys'))
		apikey.delete()
		return HttpResponseRedirect(reverse('thingstore.views.settings_apikeys'))
