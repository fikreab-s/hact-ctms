"""Clinical serializers — clinical schema."""

from rest_framework import serializers

from .models import (
    Form, FormInstance, Item, ItemResponse, Query,
    Site, Study, Subject, SubjectVisit, Visit,
)


class StudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class VisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SubjectVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectVisit
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class FormInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormInstance
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ItemResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemResponse
        fields = "__all__"
        read_only_fields = ("id", "updated_at")


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "raised_at")
