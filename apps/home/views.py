from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader

@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    group = None
    if request.user.groups.exists():
        group = request.user.groups.all()[0].name

    if group == 'Admin':
        html_template = loader.get_template('home/index.html')
        return HttpResponse(html_template.render(context, request))
    
    elif group == 'Guest':
        html_template = loader.get_template('home/index-guest.html')
        return HttpResponse(html_template.render(context, request))
    
    else:
        html_template = loader.get_template('home/page-403.html')
        return HttpResponseForbidden(html_template.render(context, request))
