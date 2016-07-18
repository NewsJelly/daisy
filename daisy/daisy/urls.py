"""daisy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from rest_framework_proxy.views import ProxyView


urlpatterns = [
    url(r'^{}admin/'.format(settings.POSTFIX), admin.site.urls),
    url(r'^{}api/'.format(settings.POSTFIX), include('api.urls')),
    url(r'^{}api/(?P<url>.*)$'.format(settings.POSTFIX),
        ProxyView.as_view(source='api/%(url)s')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += [
    url(r'^{}.*'.format(settings.POSTFIX),
        TemplateView.as_view(template_name='index.html'),
        name='index'),
]
