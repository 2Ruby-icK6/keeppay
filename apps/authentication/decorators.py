from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect
from django import template
from django.template import loader
from django.urls import reverse

def unauthorized_user(view_func):
    def wrapper_func(request, *args, **kwags):
        if request.user.is_authenticated:
            return redirect('home')
        
        else:
            return view_func(request, *args, **kwags)
    
    return wrapper_func


# def guest_required(view_func):
#     """
#     Decorator to restrict access to certain views for guests (non-authenticated users).
#     """
#     def _wrapped_view(request, *args, **kwargs):
#         if request.user.is_authenticated:
#             # If the user is authenticated, redirect to dashboard or profile page
#             if request.user.is_superuser:
#                 return HttpResponseRedirect(reverse('admin:index'))  # Redirect admin to admin dashboard
#             else:
#                 return HttpResponseRedirect(reverse('dashboard'))  # Redirect guest to dashboard
#         return view_func(request, *args, **kwargs)
#     return _wrapped_view

# def admin_required(view_func):
#     """
#     Decorator to restrict access to certain views for admin users.
#     """
#     def _wrapped_view(request, *args, **kwargs):
#         if request.user.is_authenticated and request.user.is_superuser:
#             return view_func(request, *args, **kwargs)
#         else:
#             return HttpResponseRedirect(reverse('login'))  # Redirect non-admins to login page
#     return _wrapped_view

def allowed_user(roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwags):
            
            group = None
            context = {}
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            
            if group in roles:
                return view_func(request, *args, **kwags)
            
            else:
                html_template = loader.get_template('home/page-403.html')
                return HttpResponse(html_template.render(context, request))
                      
        return wrapper_func
    return decorator

def admin_only(view_func):
    def wrapper_func(request, *args, **kwags):
            
        group = None
        context = {}
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
            
        if group == "Guest":
            return redirect("index_guest")
        
        if group == "Admin":
            return view_func(request, *args, **kwags)
        
        else: 
            html_template = loader.get_template('home/page-404.html')
            return HttpResponse(html_template.render(context, request))
        
    return wrapper_func