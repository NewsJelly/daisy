# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from collections import OrderedDict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.admin.models import LogEntry, DELETION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.utils.encoding import force_unicode, force_text

from rest_framework import exceptions
from rest_framework import filters
from rest_framework import status
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import pagination
from rest_framework import authentication
from rest_framework.response import Response

from djoser.views import PasswordResetView, SetUsernameView

from .permissions import IsOwnerOrReadOnly, IsOwner

from .models import Category, CategoryIcon
from .models import Project, Data, VisualizeType
from .models import ProfileImage

from .serializers import CategorySerializer, CategoryIconSerializer
from .serializers import ProjectSerializer, DataSerializer,\
    DataOriginSerializer, VisualizeTypeSerializer, ListProjectSerializer
from .serializers import ProfileImageSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class SessionAuthentication(authentication.SessionAuthentication):
    def enforce_csrf(self, request):
        return


class ProjectPagination(pagination.PageNumberPagination):
    page_size = 6
    paginate_by_param = 'page_size'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('num_pages', self.page.paginator.num_pages),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class DefaultReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    authentication_classes: 인증과 관련된 부분
    permission_classes: API 사용을 허가를 결정
    renderer_classes: API 출력과 관련된 부분 (JSON, HTML 등 지원)
    filter_backends: 검색과 관련된 부분(search= 혹은 {key}= 형식
    """
    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication,
        # authentication.SessionAuthentication,
    )
    permission_classes = (
        IsOwnerOrReadOnly,
    )

    if not settings.DEBUG:
        from rest_framework.renderers import JSONRenderer

        renderer_classes = (
            JSONRenderer,
        )

    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
    )


class DefaultViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     DefaultReadOnlyViewSet):
    pass


class LoggerViewSet(DefaultViewSet):
    """
    삭제/갱신 시에 로그 저장
    """
    def _logging(self, request, instance, action_flag):
        message = {
            DELETION: 'Deleted {verbose_name} "{instance}"',
            CHANGE: 'Changed {data} for {verbose_name} "{instance}"'
        }

        change_message = {
            'verbose_name': force_text(instance._meta.verbose_name),
            'instance': force_text(instance)
        }

        if action_flag == CHANGE:
            change_message.update({'data': force_text(request.data)})

        try:
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(instance).pk,
                object_id=instance.pk,
                object_repr=force_unicode(instance),
                action_flag=action_flag,
                change_message=message[action_flag].format(**change_message)
            )
        except Exception as ex:
            logger.error(ex)
            print ex


    @method_decorator(csrf_protect)
    def create(self, request, *args, **kwargs):
        response = super(DefaultViewSet, self).create(
            request, *args, **kwargs
        )
        return response

    @method_decorator(csrf_protect)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super(DefaultViewSet, self).update(
            request, *args, **kwargs
        )

        if response.status_code == status.HTTP_200_OK:
            self._logging(request, instance, CHANGE)
        return response

    @method_decorator(csrf_protect)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super(DefaultViewSet, self).destroy(
            request, *args, **kwargs
        )

        if response.status_code == status.HTTP_204_NO_CONTENT:
            self._logging(request, instance, DELETION)
        return response


class CategoryIconViewSet(LoggerViewSet):
    queryset = CategoryIcon.objects.all()
    serializer_class = CategoryIconSerializer
    filter_fields = ('title', )


class CategoryViewSet(LoggerViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProjectViewSet(LoggerViewSet):
    """
    프로젝트 목록을 보여주며 최근 발행한 프로젝트 목록부터 보여준다.
    프로젝트 상태(임시 저장, 발행)에 따른 목록을 따로 보여줄 수 있다.
    특정 프로젝트를 조회할 때 조회수(hits)가 자동으로 증가한다.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = ProjectPagination
    filter_fields = ('status', )

    def list(self, request, *args, **kwargs):
        self.serializer_class = ListProjectSerializer
        queryset = self.filter_queryset(self.get_queryset()).filter(status=Project.STATUS_PUBLISHED)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        instance.hits += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MyProjectViewSet(ProjectViewSet):
    permission_classes = (
        IsOwner,
    )

    def list(self, request, *args, **kwargs):
        user = self.request.user
        self.serializer_class = ListProjectSerializer
        queryset = self.filter_queryset(self.get_queryset().filter(user_id=user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class DataViewSet(LoggerViewSet):
    queryset = Data.objects.all()
    serializer_class = DataSerializer


class DataOriginViewSet(DefaultReadOnlyViewSet):
    queryset = Data.objects.all()
    serializer_class = DataOriginSerializer

    def list(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(request.method)


class VisualizeTypeViewSet(LoggerViewSet):
    queryset = VisualizeType.objects.all()
    serializer_class = VisualizeTypeSerializer


class ProfileImageViewSet(LoggerViewSet):
    queryset = ProfileImage.objects.all()
    serializer_class = ProfileImageSerializer

    permission_classes = (
        IsOwner,
    )

    def list(self, request, *args, **kwargs):
        user = self.request.user
        queryset = self.filter_queryset(self.get_queryset().filter(user_id=user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DaisyPasswordResetView(PasswordResetView):
    plain_body_template_name = None
    html_body_template_name = 'password_reset_email_body.html'


class DaisySetUsernameView(SetUsernameView):
    def action(self, serializer):
        self.request.user.first_name = serializer.data['new_username']
        if 'new_email' in serializer.data:
            if User.objects.get(username=serializer.data['new_email']):
                return Response({'detail': u'이미 사용 중인 이메일입니다.'}, status=status.HTTP_400_BAD_REQUEST)
            self.request.user.email = serializer.data['new_email']
            self.request.user.username = serializer.data['new_email']
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
