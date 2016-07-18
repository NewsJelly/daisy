# -*- coding: utf-8 -*-
from django.conf import settings

from . import views

if settings.DEBUG:
    from rest_framework.routers import DefaultRouter
    router = DefaultRouter(trailing_slash=False)
else:
    from rest_framework.routers import SimpleRouter
    router = SimpleRouter(trailing_slash=False)

router.register(r'category-icon', views.CategoryIconViewSet)
router.register(r'category', views.CategoryViewSet)
router.register(r'project', views.ProjectViewSet)
router.register(r'data', views.DataOriginViewSet)
router.register(r'visualize-type', views.VisualizeTypeViewSet)
urlpatterns = router.urls
