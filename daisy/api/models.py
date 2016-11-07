# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class CategoryIcon(models.Model):
    """카테고리에 사용되는 아이콘 목록"""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, null=False, unique=True)
    image = models.ImageField(null=False,
                              upload_to='uploaded_images/category_icons/')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'category_icon'

    @property
    def get_absolute_image_url(self):
        return '{}{}'.format(MEDIA_URL, self.image.url)

    def __unicode__(self):
        return '{} - {}'.format(self.__class__.__name__, self.id)

    def image_tag(self):
        return '<img src="{}" />'.format(self.image.url)

    image_tag.short_description = 'Image Preview'
    image_tag.allow_tags = True


@receiver(models.signals.pre_save, sender=CategoryIcon)
def auto_delete_file_on_change_from_category_icon(sender, instance, **kwargs):
    """category_icon 테이블이 갱신되는 경우 저장된 파일을 함께 삭제한다.
    :param sender: 신호
    :param instance: CategoryIcon의 인스턴스
    :param kwargs: dict
    """
    if not instance.pk:
        return False

    try:
        old_image = CategoryIcon.objects.get(pk=instance.pk).image
    except CategoryIcon.DoesNotExist:
        return False

    new_image = instance.image

    if old_image and old_image != new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)


@receiver(models.signals.post_delete, sender=CategoryIcon)
def auto_delete_file_on_delete_from_category_icon(sender, instance, **kwargs):
    """category_icon 테이블에서 삭제되는 경우 저장된 파일도 함께 삭제한다.
    :param sender: 신호
    :param instance: CategoryIcon의 인스턴스
    :param kwargs: dict
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


class Category(models.Model):
    """카테고리 목록"""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, null=False, unique=True)
    description = models.CharField(max_length=1024, blank=True)
    category_icon = models.ForeignKey(
        CategoryIcon,
        related_name='category_icon'
    )
    code = models.CharField(max_length=6, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'category'

    def __unicode__(self):
        return '{} - {}'.format(self.__class__.__name__, self.id)


###############################################################################
class Project(models.Model):
    """프로젝트 목록"""
    STATUS_DRAFT = 1
    STATUS_PUBLISHED = 2
    STATUS_CHOICES = (
        (STATUS_DRAFT, _('draft')),
        (STATUS_PUBLISHED, _('published')),
    )

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, null=False)
    user = models.ForeignKey(User, related_name='project')
    description = models.CharField(max_length=1024, blank=True)
    status = models.SmallIntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT
    )
    hits = models.IntegerField(default=0)
    copyright = models.CharField(max_length=100, blank=True)
    published = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project'
        ordering = ['-published']

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_PUBLISHED and self.published is None:
            self.published = timezone.now()
        super(Project, self).save(*args, **kwargs)


class VisualizeType(models.Model):
    """시각화 유형
    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, null=False, unique=True)
    alias = models.CharField(max_length=100, null=False, unique=True)
    image = models.ImageField(null=True,
                              upload_to='uploaded_images/visualize_type/')
    attribute = models.TextField()
    sample_image = models.ImageField(null=True,
                                     upload_to='uploaded_images/sample_data/')
    setting_image = models.ImageField(null=True,
                                      upload_to='uploaded_images/setting_data/')
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'visualize_type'
        ordering = ['id']

    @property
    def get_absolute_image_url(self):
        return '{}{}'.format(MEDIA_URL, self.image.url)

    @property
    def get_absolute_sample_image_url(self):
        return '{}{}'.format(MEDIA_URL, self.sample_image.url)

    @property
    def get_absolute_setting_image_url(self):
        return '{}{}'.format(MEDIA_URL, self.setting_image.url)

    def __unicode__(self):
        return self.title

    def image_tag(self):
        return '<img src="{}" />'.format(self.image.url)

    def sample_image_tag(self):
        return '<img src="{}" />'.format(self.sample_image.url)

    def setting_image_tag(self):
        return '<img src="{}" />'.format(self.setting_image.url)

    image_tag.short_description = 'Chart Image'
    image_tag.allow_tags = True

    sample_image_tag.short_description = 'Sample Data'
    sample_image_tag.allow_tags = True

    setting_image_tag.short_description = 'Setting Data'
    setting_image_tag.allow_tags = True


@receiver(models.signals.pre_save, sender=VisualizeType)
def auto_delete_file_on_change_from_visualize_type(sender, instance, **kwargs):
    """visualize_type 테이블이 갱신되는 경우 저장된 파일을 함께 삭제한다.
    :param sender: 신호
    :param instance: VisualizeType의 인스턴스
    :param kwargs: dict
    """
    if not instance.pk:
        return False

    try:
        old_image = VisualizeType.objects.get(pk=instance.pk).image
        old_sample = VisualizeType.objects.get(pk=instance.pk).sample_image
        old_setting = VisualizeType.objects.get(pk=instance.pk).setting_image
    except VisualizeType.DoesNotExist:
        return False

    new_image = instance.image
    new_sample = instance.sample_image
    new_setting = instance.setting_image

    if old_image and old_image != new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)

    if old_sample and old_sample != new_sample:
        if os.path.isfile(old_sample.path):
            os.remove(old_sample.path)

    if old_setting and old_setting != new_setting:
        if os.path.isfile(old_setting.path):
            os.remove(old_setting.path)


@receiver(models.signals.post_delete, sender=VisualizeType)
def auto_delete_file_on_delete_from_visualize_type(sender, instance, **kwargs):
    """visualize_type 테이블에서 삭제되는 경우 저장된 파일도 함께 삭제한다.
    :param sender: 신호
    :param instance: VisualizeType의 인스턴스
    :param kwargs: dict
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

    if instance.sample_image:
        if os.path.isfile(instance.sample_image.path):
            os.remove(instance.sample_image.path)

    if instance.setting_image:
        if os.path.isfile(instance.setting_image.path):
            os.remove(instance.setting_image.path)


class Visualize(models.Model):
    """시각화 모델(그래프)
    """
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='visualize'
    )
    order = models.IntegerField(default=0)
    visualize_type = models.ForeignKey(
        VisualizeType,
        related_name='visualize'
    )
    attribute = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'visualize'
        ordering = ['order']

    def __unicode__(self):
        return u'{}'.format(self.project.title)


class Filter(models.Model):
    """시각화에서 사용하는 필터"""

    id = models.OneToOneField(
        Visualize,
        db_column='id',
        on_delete=models.CASCADE,
        primary_key=True
    )
    content = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'filter'

    def __unicode__(self):
        return u'{}'.format(self.id)


class Data(models.Model):
    """시각화에서 사용하는 데이터"""
    TYPE_UPLOAD = 1
    TYPE_QUERY = 2
    TYPE_API = 3
    TYPE_DB = 4
    STATUS_CHOICES = (
        (TYPE_UPLOAD, _('upload')),
        (TYPE_QUERY, _('query')),
        (TYPE_API, _('api')),
        (TYPE_DB, _('db')),
    )

    id = models.OneToOneField(
        Visualize,
        db_column='id',
        on_delete=models.CASCADE,
        primary_key=True
    )
    type = models.SmallIntegerField(choices=STATUS_CHOICES)
    visualize_data = models.TextField(null=False)
    origin_data = models.TextField(null=True)
    metadata = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'data'

    def __unicode__(self):
        return u'{}'.format(self.id)


class Thumbnail(models.Model):
    """시각화 모델(그래프)의 썸네일"""
    id = models.OneToOneField(
        Visualize,
        db_column='id',
        on_delete=models.CASCADE,
        primary_key=True
    )
    image = models.TextField(null=True, blank=True)
    image_path = models.ImageField(null=True,
                                   blank=True,
                                   upload_to='uploaded_images/thumbnails/')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'thumbnail'

    def __unicode__(self):
        return u'{}'.format(self.id)

    def image_tag(self):
        return '<img src="{}" />'.format(self.image)

    image_tag.short_description = 'Image Preview'
    image_tag.allow_tags = True

    @property
    def get_absolute_image_url(self):
        return '{}{}'.format(MEDIA_URL, self.image_path.url)

    def save(self, *args, **kwargs):
        if self.image:
            self.image_path = self.make_image_file()
            super(Thumbnail, self).save(*args, **kwargs)

    def make_image_file(self):
        try:
            fmt, imgstr = self.image.split(';base64,')
            ext = fmt.split('/')[-1]

            file_name = '{}.{}'.format(self.id.id, ext)

            return ContentFile(
                imgstr.decode('base64'),
                name=file_name
            )
        except:
            return None


@receiver(models.signals.post_delete, sender=Thumbnail)
def auto_delete_file_on_delete_from_thumbnail(sender, instance, **kwargs):
    """thumbnail 테이블에서 삭제되는 경우 저장된 파일도 함께 삭제한다."""
    if instance.image_path:
        if os.path.isfile(instance.image_path.path):
            os.remove(instance.image_path.path)


###############################################################################
class ProfileImage(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    image = models.ImageField(null=True,
                              blank=True,
                              upload_to='uploaded_images/profile/')
    image_base64 = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profile_image'


@receiver(models.signals.pre_save, sender=ProfileImage)
def auto_delete_file_on_change_from_profile_image(sender, instance, **kwargs):
    """profile_image 테이블이 갱신되는 경우 저장된 파일을 함께 삭제한다.
    :param sender: 신호
    :param instance: ProfileImage의 인스턴스
    :param kwargs: dict
    """
    if not instance.pk:
        return False

    try:
        old_image = ProfileImage.objects.get(pk=instance.pk).image
    except ProfileImage.DoesNotExist:
        return False

    new_image = instance.image

    if old_image and old_image != new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)


@receiver(models.signals.post_delete, sender=ProfileImage)
def auto_delete_file_on_delete_from_profile_image(sender, instance, **kwargs):
    """profile_image 테이블에서 삭제되는 경우 저장된 파일도 함께 삭제한다.
    :param sender: 신호
    :param instance: ProfileImage의 인스턴스
    :param kwargs: dict
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
