# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url

from . import views

if settings.DEBUG:
    from rest_framework.routers import DefaultRouter
    router = DefaultRouter(trailing_slash=False)
else:
    from rest_framework.routers import SimpleRouter
    router = SimpleRouter(trailing_slash=False)

urlpatterns = [
    url(r'^auth/username/$', views.DaisySetUsernameView.as_view(), name='set_username'),
    url(r'^auth/password/reset/$', views.DaisyPasswordResetView.as_view(), name='password_reset'),
    url(r'^auth/', include('djoser.urls.authtoken')),
]
router.register(r'category-icon', views.CategoryIconViewSet)
router.register(r'category', views.CategoryViewSet)
router.register(r'project', views.ProjectViewSet, base_name='project')
router.register(r'myproject', views.MyProjectViewSet, base_name='myproject')
router.register(r'data', views.DataOriginViewSet)
router.register(r'visualize-type', views.VisualizeTypeViewSet)
router.register(r'profile-image', views.ProfileImageViewSet)
urlpatterns += router.urls
