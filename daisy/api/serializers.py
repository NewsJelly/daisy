# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import os
import unicodedata
from collections import OrderedDict

from django.contrib.auth import authenticate, get_user_model
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.reverse import reverse

from djoser.serializers import LoginSerializer

from .models import Category, CategoryIcon
from .models import Project, Filter, Data, Thumbnail, VisualizeType, Visualize
from .models import ProfileImage


User = get_user_model()
logger = logging.getLogger(__name__)


class JSONSerializerField(serializers.Field):
    def to_internal_value(self, data):
        return json.dumps(data)

    def to_representation(self, obj):
        return json.loads(obj) if obj else None


class LoggerSerializer(serializers.ModelSerializer):
    """로그를 기록하기 위한 클래스"""

    def _logging(self, instance, message, action_flag, user=None):
        try:
            LogEntry.objects.log_action(
                user_id=user if user else self.context['request'].user.pk,
                content_type_id=ContentType.objects.get_for_model(instance).pk,
                object_id=instance.pk,
                object_repr=force_text(instance),
                action_flag=action_flag,
                change_message=message,
            )
        except Exception as ex:
            logger.error(ex)

    def create(self, validated_data):
        instance = super(LoggerSerializer, self).create(validated_data)
        if instance.pk:
            message = 'Added {0} "{1}"'.format(
                force_text(instance._meta.verbose_name),
                force_text(instance)
            )
            self._logging(instance, message, ADDITION)
        return instance


class CategoryIconSerializer(LoggerSerializer):
    """ 카테고리 아이콘을 직렬화하는 클래스"""
    class Meta:
        model = CategoryIcon
        fields = ('id', 'title', 'image', )

    def update(self, instance, validated_data):
        """카테고리 아이콘 항목을 갱신할 때 기존 파일을 삭제하고 새로운 내용으로 저장한다.
        :param instance: 기존 인스턴스
        :param validated_data: 변경된 값들
        :rtype: instance: 갱신된 인스턴스
        """
        if instance.image:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)

        instance.title = validated_data.get('title', instance.title)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance


class CategorySerializer(LoggerSerializer):
    """ 카테고리를 직렬화하는 클래스"""
    links = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'title', 'description', 'category_icon', 'code',
                  'links', )

    def get_links(self, obj):
        request = self.context['request']
        links = {
            'category-icon': None
        }
        if obj.category_icon:
            links['category-icon'] = reverse(
                'categoryicon-detail',
                kwargs={'pk': obj.category_icon.id}, request=request)
        return links


###############################################################################
class VisualizeTypeSerializer(LoggerSerializer):
    """ 시각화 형식을 직렬화하는 클래스"""
    class Meta:
        model = VisualizeType
        fields = ('id', 'title', 'alias', 'image', 'attribute',
                  'sample_image', 'setting_image', 'description', )


class DataOriginSerializer(LoggerSerializer):
    """시각화에 사용하는 데이터를 직렬화하는 클래스"""
    origin_data = JSONSerializerField()

    class Meta:
        model = Data
        fields = ('id', 'origin_data', )


class FilterSerializer(LoggerSerializer):
    """시각화에 사용하는 필터를 직렬화하는 클래스"""
    content = JSONSerializerField()

    class Meta:
        model = Filter
        fields = ('content', )


class DataSerializer(LoggerSerializer):
    """시각화에 사용하는 데이터를 직렬화하는 클래스"""
    visualize_data = JSONSerializerField()
    origin_data = JSONSerializerField(write_only=True)
    metadata = JSONSerializerField()

    class Meta:
        model = Data
        fields = ('type', 'visualize_data', 'origin_data', 'metadata', )


class ThumbnailSerializer(LoggerSerializer):
    """ 썸네일을 직렬화하는 클래스"""
    class Meta:
        model = Thumbnail
        fields = ('image', )


class VisualizeSerializer(LoggerSerializer):
    """ 시각화 항목을 직렬화하는 클래스"""
    data = DataSerializer()
    filter = FilterSerializer(required=False)
    thumbnail = ThumbnailSerializer(required=False)
    attribute = JSONSerializerField()
    # thumbnail_link = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Visualize
        fields = (
            'id', 'order', 'data', 'filter', 'thumbnail', 'visualize_type',
            'type', 'attribute',
        )
        extra_kwargs = {'visualize_type': {'write_only': True}}

    def get_type(self, obj):
        """
        :param obj: 인스턴스
        :rtype type: 썸네일 링크 주소
        """
        type = {
            'title': obj.visualize_type.title,
            'alias': obj.visualize_type.alias,
            'attribute': obj.visualize_type.attribute,
        }
        return type


class ProjectSerializer(LoggerSerializer):
    user = serializers.SlugRelatedField(
        slug_field=User.USERNAME_FIELD,
        queryset=User.objects.all()
    )
    visualize = VisualizeSerializer(many=True)
    hits = serializers.ReadOnlyField()
    published = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = ('id', 'title', 'user', 'description', 'visualize',
                  'status', 'hits', 'copyright', 'published', )

    def create(self, validated_data):
        try:
            visualizes_data = validated_data.pop('visualize')
        except:
            visualizes_data = []

        # create project
        instance = Project.objects.create(**validated_data)

        for visualize_data in visualizes_data:
            data_data = visualize_data.pop('data')
            filter_data = visualize_data.pop('filter')
            thumbnail_data = visualize_data.pop('thumbnail') if 'thumbnail' in visualize_data else {}

            visualize = Visualize.objects.create(
                project=instance,
                **visualize_data
            )

            temp = json.loads(data_data['metadata'])
            temp['title'] = unicodedata.normalize('NFC', temp['title'])
            data_data['metadata'] = json.dumps(temp)

            Data.objects.create(id=visualize, **data_data)
            Filter.objects.create(id=visualize, **filter_data)
            Thumbnail.objects.create(id=visualize, **thumbnail_data)

        if instance.pk:
            message = 'Added {0} "{1}"'.format(
                force_text(instance._meta.verbose_name),
                force_text(instance))
            self._logging(instance, message, ADDITION)
        return instance

    def update(self, instance, validated_data):
        if 'visualize' in validated_data:
            visualizes_data = validated_data.pop('visualize')

            # update visulize
            visualize_list = Visualize.objects.filter(project_id=instance.pk)
            visualize_mapping = {v.order: v for v in visualize_list}
            data_mapping = {item['order']: item for item in visualizes_data}

            for v_id, data in data_mapping.items():
                data_data = data.pop('data')
                filter_data = data.pop('filter')
                thumbnail_data = data.pop('thumbnail') if 'thumbnail' in data else {}

                v = visualize_mapping.get(v_id, None)
                obj, created = Visualize.objects.update_or_create(
                    project=instance, order=v_id, defaults=data)
                Data.objects.update_or_create(id=obj, defaults=data_data)
                Filter.objects.update_or_create(id=obj, defaults=filter_data)

                # 썸네일 파일이 있는 경우 삭제한다.
                self.delete_thumbnail(obj)
                Thumbnail.objects.update_or_create(
                    id=obj,
                    defaults=thumbnail_data
                )

            for v_id, v in visualize_mapping.items():
                if v_id not in data_mapping:
                    self.delete_thumbnail(v)
                    v.delete()

        # update project
        instance.title = validated_data.get('title', instance.title)
        instance.user = validated_data.get('user', instance.user)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        instance.copyright = validated_data.get(
            'copyright', instance.copyright)
        instance.save()

        return instance

    def delete_thumbnail(self, obj):
        try:
            thumbnail = Thumbnail.objects.get(pk=obj.pk)
            if thumbnail.image_path:
                if os.path.isfile(thumbnail.image_path.path):
                    os.remove(thumbnail.image_path.path)
        except Thumbnail.DoesNotExist as e:
            logger.error(e)


class ListVisualizeSerializer(LoggerSerializer):
    thumbnail = ThumbnailSerializer(read_only=True)

    class Meta:
        model = Visualize
        fields = ('id', 'thumbnail', )


class ListProjectSerializer(LoggerSerializer):
    user = serializers.SlugRelatedField(
        slug_field=User.USERNAME_FIELD,
        queryset=User.objects.all()
    )
    visualize = ListVisualizeSerializer(many=True)
    hits = serializers.ReadOnlyField()
    published = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = ('id', 'title', 'user', 'description', 'visualize',
                  'status', 'hits', 'copyright', 'published', )


class DuplicatedError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _(u'사용자가 이미 존재합니다.')


class NotRegisteredError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _(u'가입되지 않은 이메일입니다.')


class PasswordError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _(u'비밀번호가 틀렸습니다.')


class DaisyUserSerializer(LoggerSerializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'},
                                     write_only=True)

    class Meta:
        model = User

    def validate(self, data):
        try:
            if User.objects.get(username=data['email']):
                raise DuplicatedError()
        except User.DoesNotExist:
            return data

    def create(self, validated_data):
        user = User(username=validated_data['email'],
                    email=validated_data['email'],
                    first_name=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user

    def to_representation(self, obj):
        return OrderedDict([
            ('id', obj.pk),
            ('username', obj.first_name),
            ('email', obj.email),
        ])


class DaisyLoginSerializer(LoginSerializer):
    def validate(self, attrs):
        self.user = authenticate(username=attrs.get(User.USERNAME_FIELD), password=attrs.get('password'))
        if self.user:
            if not self.user.is_active:
                raise serializers.ValidationError(self.error_messages['inactive_account'])
            return attrs
        else:
            try:
                if User.objects.get(username=attrs.get(User.USERNAME_FIELD)):
                    raise PasswordError()
            except User.DoesNotExist:
                raise NotRegisteredError()


class DaisySetUsernameSerializer(LoggerSerializer):
    new_email = serializers.EmailField(required=False)
    new_username = serializers.CharField()

    class Meta(object):
        model = User
        fields = ('new_email', 'new_username', )


class ProfileImageSerializer(LoggerSerializer):
    user = serializers.SlugRelatedField(
        slug_field=User.USERNAME_FIELD,
        queryset=User.objects.all()
    )

    class Meta:
        model = ProfileImage
        fields = ('id', 'user', 'image', )
