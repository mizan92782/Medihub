from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from location.models import Division, District, Upozila, Union
from core.api_response import APIResponse
from core.pagination import StandardResultsSetPagination
from rest_framework import serializers


class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = '__all__'


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'


class UpozilaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upozila
        fields = '__all__'


class UnionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Union
        fields = '__all__'


class DivisionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer
    permission_classes = [AllowAny]


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['division']
    search_fields = ['district_name_eng', 'district_name_bn']


class UpozilaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Upozila.objects.all()
    serializer_class = UpozilaSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['district']
    search_fields = ['upozila_name_eng', 'upoila_name_bn']


class UnionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Union.objects.all()
    serializer_class = UnionSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['upozila']
    search_fields = ['union_name_eng', 'union_name_bn']


def union_list(request):
    upazila_id = request.GET.get('upazila')
    qs = Union.objects.all()
    if upazila_id:
        qs = qs.filter(upozila_id=upazila_id)
    unions = list(qs.values('id', 'union', 'union_name_bn', 'union_name_eng'))
    return Response({'count': len(unions), 'unions': unions})
