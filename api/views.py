from datetime import timedelta, datetime
from django.db.models.aggregates import Sum, Count
from django.conf import settings
import urllib
import json
from django.db.models import Q
import os
from dyn import get_data

from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import generics, mixins, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
import pymysql
from api import serializers
from api.serializers import UserSerializer
from main import models
from main.models import WellMatrix
from main.serializers import WellMatrixCreateSerializer, WellMatrixSerializer, WellSerializer, FieldSerializer, \
    FieldBalanceSerializer, FieldBalanceCreateSerializer, DepressionSerializer, TSSerializer, ProdProfileSerializer, \
    GSMSerializer, DynamogramSerializer, ImbalanceSerializer, ImbalanceHistorySerializer, \
    ImbalanceHistoryAllSerializer, SumWellInFieldSerializer, WellEventsSerializer, FieldMatrixSerializer, \
    ConstantSerializer, RecommendationSerializer, EventsSerializer, WattmetrogramSerializer
from django.core.mail import EmailMessage
from django.db.models import Sum, Avg
import cx_Oracle
import pyodbc
import smtplib


class AuthView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })


class ListUser(generics.ListCreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


class Constant(generics.ListAPIView):
    queryset = models.Constant.objects.all()
    serializer_class = ConstantSerializer


class ImbalanceHistoryAll(generics.ListAPIView):
    queryset = models.ImbalanceHistoryAll.objects.all().order_by('-timestamp')[:30]
    serializer_class = ImbalanceHistoryAllSerializer


class SumWellInFieldSerializerAll(generics.ListAPIView):
    dt = datetime(2021, 1, 1)
    queryset = models.SumWellInField.objects.filter(timestamp__gte=dt).order_by('-timestamp')[:240]
    serializer_class = SumWellInFieldSerializer


class FieldMatrixSerializerAll(generics.ListAPIView):
    dt = datetime(2021, 1, 1)
    queryset = models.FieldMatrix.objects.filter(timestamp__gte=dt).order_by('timestamp')
    serializer_class = FieldMatrixSerializer


class DetailUser(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


class WellMatrixViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('well',)
    queryset = models.WellMatrix.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        # if self.request.user.type == User.CLIENT:
        #     return models.Application.objects.filter(user=self.request.user)
        return models.WellMatrix.objects.filter(timestamp=timezone.now(), well__has_isu=True).order_by('well__gzu', 'well__horizon')

    def get_serializer_class(self):
        if self.action == 'create_wellmatrix':
            return WellMatrixCreateSerializer
        return WellMatrixSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_all(self, request, *args, **kwargs):
        result = models.WellMatrix.objects.filter(timestamp=timezone.now())
        return Response(WellMatrixSerializer(result, many=True).data)

    @action(methods=['get'], detail=False)
    def get_by_well(self, request, *args, **kwargs):
        dt = datetime(2021, 1, 1)
        well = models.Well.objects.get(name=request.GET.get("well"))
        result = models.WellMatrix.objects.filter(timestamp__gte=dt, well=well).order_by('-timestamp')
        return Response(WellMatrixSerializer(result, many=True).data)

    @action(methods=['get'], detail=False)
    def get_by_well_period(self, request, *args, **kwargs):
        well = models.Well.objects.get(name=request.GET.get("well"))
        beg_year = int(request.GET.get("year"))
        beg_month = int(request.GET.get("month"))
        beg_dt = datetime(beg_year, beg_month, 1)
        end_year = beg_year
        end_month = beg_month + 1
        if end_month == 13:
            end_month = 1
            end_year = end_year + 1
        end_dt = datetime(end_year, end_month, 1)

        result = models.WellMatrix.objects.filter(timestamp__gte=beg_dt, timestamp__lte=end_dt, well=well).order_by('-timestamp')
        return Response(WellMatrixSerializer(result, many=True).data)

    @action(methods=['get'], detail=False)
    def get_by_field(self, request, *args, **kwargs):
        field = models.Field.objects.get(name=request.GET.get("field"))
        result = models.WellMatrix.objects.filter(well__field=field)
        return Response(WellMatrixSerializer(result, many=True).data)


class WellEventsViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_date = datetime(2021, 1, 1)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('well',)
    queryset = models.WellEvents.objects.filter(beg__gte=filter_date).order_by('-beg')[:100]

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        filter_date = datetime(2021, 1, 1)
        return models.WellEvents.objects.filter(beg__gte=filter_date).order_by('-beg')[:100]

    def get_serializer_class(self):
        return WellEventsSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_well(self, request, *args, **kwargs):
        well = models.Well.objects.get(name=request.GET.get("well"))
        filter_date = datetime(2021, 1, 1)
        result = models.WellEvents.objects.filter(beg__gte=filter_date, well=well).order_by('-beg')[:100]
        return Response(WellEventsSerializer(result, many=True).data)

    @action(methods=['get'], detail=False)
    def get_by_field(self, request, *args, **kwargs):
        field = models.Field.objects.get(pk=request.GET.get("field"))
        filter_date = datetime(2021, 1, 1)
        result = models.WellEvents.objects.filter(beg__gte=filter_date, well__field=field).order_by('-beg')[:100]
        return Response(WellEventsSerializer(result, many=True).data)

    @action(methods=['get'], detail=False)
    def get_events_count(self, request, *args, **kwargs):
        filter_date = datetime(2021, 1, 1)
        data = dict()
        data[0] = {'gtm': models.WellEvents.objects.filter(beg__gte=filter_date, event_type=models.WellEvents.GTM).count(),
                   'krs': models.WellEvents.objects.filter(beg__gte=filter_date, event_type=models.WellEvents.KRS).count(),
                   'all': models.WellEvents.objects.filter(beg__gte=filter_date).count(),
                   'gtm_wells': models.WellEvents.objects.filter(beg__gte=filter_date, event_type=models.WellEvents.GTM).distinct('well').count(),
                   'all_wells': models.WellEvents.objects.filter(beg__gte=filter_date).distinct('well').count()}
        for field in models.Field.objects.all():
            data[field.pk] = {'gtm': models.WellEvents.objects.filter(beg__gte=filter_date, well__field=field, event_type='ГТМ').count(),
                              'krs': models.WellEvents.objects.filter(beg__gte=filter_date, well__field=field, event_type='КРС').count(),
                              'all': models.WellEvents.objects.filter(beg__gte=filter_date, well__field=field).count(),
                              'gtm_wells': models.WellEvents.objects.filter(beg__gte=filter_date, well__field=field, event_type='ГТМ').distinct('well').count(),
                              'all_wells': models.WellEvents.objects.filter(beg__gte=filter_date, well__field=field).distinct('well').count()}
        return Response(data)

    @action(methods=['get'], detail=False)
    def get_events_statistics(self, request, *args, **kwargs):
        id = request.GET.get("field")
        if id == '0':
            events = models.Events.objects.filter(field__isnull=True).order_by('-fact')[:3]
        else:
            field = models.Field.objects.get(pk=id)
            events = models.Events.objects.filter(field=field).order_by('-fact')[:3]
        return Response(EventsSerializer(events, many=True).data)


class RecommendationViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('well',)
    queryset = models.Recommendation.objects.all().order_by('-timestamp')[:10]

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.Recommendation.objects.all().order_by('-timestamp')[:10]

    def get_serializer_class(self):
        return RecommendationSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_well(self, request, *args, **kwargs):
        well = models.Well.objects.get(name=request.GET.get("well"))
        result = models.Recommendation.objects.filter(well=well).order_by('-timestamp')[:10]
        return Response(RecommendationSerializer(result, many=True).data)

    @action(methods=['get'], detail=False)
    def get_by_field(self, request, *args, **kwargs):
        field = models.Field.objects.get(pk=request.GET.get("field"))
        result = models.Recommendation.objects.filter(well__field=field).order_by('-timestamp')[:10]
        return Response(RecommendationSerializer(result, many=True).data)


class DepressionViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('well',)
    queryset = models.Depression.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return None

    def get_serializer_class(self):
        # if self.action == 'create_wellmatrix':
        #     return WellMatrixCreateSerializer
        return DepressionSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_well(self, request, *args, **kwargs):
        well = models.Well.objects.get(name=request.GET.get("well"))
        result = models.Depression.objects.filter(well=well)
        return Response(DepressionSerializer(result, many=True).data)

    @action(methods=['post'], detail=False)
    def create_depression(self, request, *args, **kwargs):
        serializer = WellMatrixCreateSerializer(data=request.data)
        if serializer.is_valid():
            well = models.Well.objects.get(name=request.data["well"])
            dt = datetime.now()
            wellmatrix = WellMatrix.objects.update_or_create(well=well, defaults={"fluid": request.data["fluid"],
                                                                                  "teh_rej_fluid": request.data["teh_rej_fluid"],
                                                                                  "teh_rej_oil": request.data["teh_rej_oil"],
                                                                                  "teh_rej_water": request.data["teh_rej_water"],
                                                                                  "gas": request.data["gas"],
                                                                                  "timestamp": dt})
            return Response(self.get_serializer(wellmatrix, many=False).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FieldBalanceViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('field',)

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return None

    def get_serializer_class(self):
        if self.action == 'create_balance':
            return FieldBalanceCreateSerializer
        return FieldBalanceSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_field(self, request, *args, **kwargs):
        field = models.Field.objects.get(name=request.GET.get("field"))
        result = models.FieldBalance.objects.filter(field=field, timestamp__year__gte=2019,
                                                    timestamp__month__gte=request.GET.get("month"),
                                                    timestamp__year__lte=2019,
                                                    timestamp__month__lte=request.GET.get("month"))
        return Response(FieldBalanceSerializer(result, many=True).data)

    @action(methods=['get'], detail=False)
    def get_total(self, request, *args, **kwargs):
        result = models.FieldBalance.objects.filter(timestamp__year__gte=2019,
                                                    timestamp__month__gte=request.GET.get("month"),
                                                    timestamp__year__lte=2019,
                                                    timestamp__month__lte=request.GET.get("month")).values('timestamp')\
            .annotate(transport_balance=Sum('transport_balance'), ansagan_balance=Sum('ansagan_balance'),
                      transport_brutto=Sum('transport_brutto'), ansagan_brutto=Sum('ansagan_brutto'),
                      transport_netto=Sum('transport_netto'), ansagan_netto=Sum('ansagan_netto'),
                      transport_density=Sum('transport_density'), ansagan_density=Sum('ansagan_density'),
                      agzu_fluid=Sum('agzu_fluid'), agzu_oil=Sum('agzu_oil'),
                      teh_rej_fluid=Sum('teh_rej_fluid'), teh_rej_oil=Sum('teh_rej_oil'))
        return Response(FieldBalanceSerializer(result, many=True).data)

    @action(methods=['post'], detail=False)
    def create_balance(self, request, *args, **kwargs):
        serializer = FieldBalanceCreateSerializer(data=request.data)
        if serializer.is_valid():
            field = models.Field.objects.get(name=request.data["field"])
            dt = datetime.now()
            balance = models.FieldBalance.objects.update_or_create(field=field, timestamp=dt,
                                                   defaults={"transport_balance": request.data["transport_balance"],
                                                             "transport_brutto": request.data["transport_brutto"],
                                                             "transport_netto": request.data["transport_netto"],
                                                             "transport_density": request.data["transport_density"]})
                                                             # "agzu_fluid": request.data["agzu_fluid"],
                                                             # "agzu_oil": request.data["agzu_oil"],
                                                             # "teh_rej_fluid": request.data["teh_rej_fluid"],
                                                             # "teh_rej_oil": request.data["teh_rej_oil"]})
            return Response(self.get_serializer(balance, many=False).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WellViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name',)
    queryset = models.Well.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.Well.objects.all()

    def get_serializer_class(self):
        return WellSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_field(self, request, *args, **kwargs):
        field = models.Field.objects.get(name=request.GET.get("field"))
        wells = models.Well.objects.filter(field=field)
        return Response(WellSerializer(wells, many=True).data)

    @action(methods=['get'], detail=False)
    def get_with_events(self, request, *args, **kwargs):
        wells = models.Well.objects.filter(rem_count__gt=0)
        return Response(WellSerializer(wells, many=True).data)

    # @action(methods=['get'], detail=False)
    # def get_with_gzu(self, request, *args, **kwargs):
    #     id = request.GET.get("field")
    #     if id == '0':
    #         wells = models.Well.objects.filter
    #     else:
    #         field = models.Field.objects.get(pk=id)
    #     wells = models.Well.objects.filter(rem_count__gt=0)
    #     return Response(WellSerializer(wells, many=True).data)


class FieldViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name',)
    queryset = models.Field.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.Field.objects.all()

    def get_serializer_class(self):
        return FieldSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class TSViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('field',)
    queryset = models.TS.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.TS.objects.all()

    def get_serializer_class(self):
        return TSSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class GSMViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('field',)
    queryset = models.GSM.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.GSM.objects.all()

    def get_serializer_class(self):
        return GSMSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class ProdProfileViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    queryset = models.ProdProfile.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.ProdProfile.objects.all()

    def get_serializer_class(self):
        return ProdProfileSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class ImbalanceViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    today = datetime.today() - timedelta(days=1)
    queryset = models.Imbalance.objects.filter(timestamp__gt=today, imbalance__gte=7, imbalance__lte=80)

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        today = datetime.today() - timedelta(days=1)
        return models.Imbalance.objects.filter(timestamp__gt=today, imbalance__gte=7, imbalance__lte=80)

    def get_serializer_class(self):
        return ImbalanceSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=True)
    def history(self, request, *args, **kwargs):
        imbalance = self.get_object()
        results = []
        for history in reversed(models.ImbalanceHistory.objects.filter(imb=imbalance).order_by('-timestamp')[:30]):
            results.append(
              ImbalanceHistorySerializer(history).data
            )
        return Response(results)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def upload_dyn_data(request):
    try:
        for well in models.Well.objects.all():
            # well = models.Well.objects.get(name=request.data["well_name"])
            # dir = 'data/' + well.name
            dir = 'data/9030'
            for x in os.walk(dir):
                for day_folder in x[1]:
                    for y in os.walk(x[0] + '/' + day_folder):
                        timestamp = datetime.strptime(day_folder, '%Y_%m_%d')
                        for hour_folder in y[1]:
                            timestamp = timestamp + timedelta(hours=int(hour_folder))
                            skv_files = os.listdir(y[0] + '/' + hour_folder)
                            for skv_file in skv_files:
                                data = get_data.ReadSKVFile(y[0] + '/' + hour_folder + '/' + skv_file)
                                if len(data.x) > 0 and len(data.y) > 0:
                                    models.Dynamogram.objects.create(well=well, timestamp=timestamp, x=data.x, y=data.y)
                                    break
                break

        return Response({
            "info": "Данные загружены"
        })
    except:
        return Response({
            "info": "Скважина не найдена"
        })


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_dyn_data(request):
    well = models.Well.objects.get(name=request.GET.get('well_name'))
    dyn = models.Dynamogram.objects.filter(well=well).order_by('-timestamp').first()
    return Response(DynamogramSerializer(dyn).data)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_watt_data(request):
    well = models.Well.objects.get(name=request.GET.get('well_name'))
    watt = models.Wattmetrogram.objects.filter(well=well).order_by('-timestamp').first()
    return Response(WattmetrogramSerializer(watt).data)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_2hour(request):
    hour_data = dict()
    hour_data['EMG'] = dict()
    hour_data['EMG']['Общее'] = []
    hour_data['EMG']['UAZ'] = []
    hour_data['EMG']['PRORVA'] = []

    conn = pymysql.connect(host='192.168.17.158', port=3306, user='root', passwd='1234', db='emg-cm', charset='utf8')
    cur = conn.cursor()

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='2:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='2:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='4:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='4:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='6:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='6:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)
    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='8:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='8:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='10:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='10:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='12:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='12:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='14:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='14:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='16:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='16:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='18:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='18:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='20:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='20:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='22:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='22:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='0:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='0:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='1:59'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='1:59'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)
    conn.close()
    return Response(hour_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def update_imbalance(request):
    wells = models.Well.objects.filter(has_isu=True)
    t = timezone.now()
    try:
        con1 = pymysql.connect(host='192.168.241.2', port=3306, user='getter', passwd='P@ssw0rD', db='sdmo', charset='utf8')
        con2 = pymysql.connect(host='192.168.243.2', port=3306, user='getter', passwd='123456', db='sdmo', charset='utf8')
        con3 = pymysql.connect(host='192.168.236.2', port=3306, user='getter', passwd='123456', db='sdmo', charset='utf8')
        con4 = pymysql.connect(host='192.168.128.2', port=3306, user='getter', passwd='123456', db='sdmo', charset='utf8')
    except:
        pass

    try:
        imbalance_history_all = models.ImbalanceHistoryAll.objects.get(timestamp__year=t.year, timestamp__month=t.month,
                                                                       timestamp__day=t.day)
        imbalance_history_all.count = 0
        imbalance_history_all.timestamp = timezone.now()
        imbalance_history_all.percent = 0
    except:
        imbalance_history_all = models.ImbalanceHistoryAll.objects.create(timestamp=timezone.now())
    for well in wells:
        try:
            if well.server == "192.168.241.2":
                cur = con1.cursor()
            elif well.server == "192.168.243.2":
                cur = con2.cursor()
            elif well.server == "192.168.236.2":
                cur = con3.cursor()
            elif well.server == "192.168.128.2":
                cur = con4.cursor()

            skv_name = well.name
            if 'VMB' in skv_name:
                skv_name = skv_name.replace('VMB', 'MLD')

            cur.execute("SELECT id FROM stations where code='" + skv_name + "' limit 1")
            row_values = cur.fetchone()
            station_id = int(row_values[0])
            cur.execute("SELECT * FROM fc_data_last where reg=30005 and station_id=" + str(station_id) + " order by savetime desc")
            row_values = cur.fetchone()
            try:
                imb = models.Imbalance.objects.get(well=well)
                try:
                    timestamp = imb.timestamp + timedelta(hours=6)
                    # if not row_values[3].strftime("%Y-%m-%d %H:%M:%S") == timestamp.strftime("%Y-%m-%d %H:%M:%S"):
                    if not row_values[3].strftime("%Y-%m-%d") == timestamp.strftime("%Y-%m-%d"):
                        imb_history = models.ImbalanceHistory.objects.create(imb=imb, well=imb.well, imbalance=imb.imbalance,
                                                                             avg_1997=imb.avg_1997, timestamp=imb.timestamp)
                        imb_history.save()
                except:
                    pass
            except:
                imb = models.Imbalance.objects.create(well=well)
            try:
                imb.imbalance = float(row_values[2])
            except:
                imb.imbalance = 0
            imb.timestamp = row_values[3]
            cur.execute("SELECT avg_1997 FROM daily_data where station_id=" + str(station_id) + " order by day desc limit 1")
            row_values = cur.fetchone()
            try:
                imb.avg_1997 = float(row_values[0])
            except:
                imb.avg_1997 = 0
            imb.save()

        except Exception as e:
            pass

    today = datetime.today() - timedelta(days=1)
    imbalance_history_all.count = models.Imbalance.objects.filter(timestamp__gt=today, imbalance__gte=7, imbalance__lte=80).count()
    imbalance_history_all.percent = (imbalance_history_all.count / models.Well.objects.filter(has_isu=True).count()) * 100
    imbalance_history_all.save()
    return Response({
        "info": "Данные загружены"
    })


def update_well(wells, server):
    err_wells_server = list()
    for w in wells:
        skv = w[0]
        if w[0] and 'MLD' in w[0]:
            skv = w[0].replace('MLD', 'VMB')
        try: 
            conn = pymysql.connect(host='192.168.17.158', port=3306, user='root', passwd='1234', db='emg-cm',
                                   charset='utf8')
            cur = conn.cursor()
            cur.execute("SELECT oil_field FROM n_well_matrix where well='" + skv + "'")
            row_values = cur.fetchone()
            if row_values is not None:
                print(skv)
                print(row_values)
                try:
                    field = models.Field.objects.get(name=row_values[0])
                except:
                    field = models.Field.objects.create(name=row_values[0])
                try:
                    well = models.Well.objects.get(name=skv, field=field)
                    print("get")
                except:
                    well = models.Well.objects.create(name=skv, field=field)
                    print("create")
                well.well_id = w[1]
                well.server = server
                well.save()
            else:
                err_wells_server.append(skv)
        except:
            err_wells_server.append(skv)
    return err_wells_server


@api_view(['GET'])
def update_wells(request):
    err_sdmo_server = list()
    err_wells_server_all = list()
    try:
        con1 = pymysql.connect(host='192.168.241.2', port=3306, user='getter', passwd='P@ssw0rD', db='sdmo', charset='utf8')
        con2 = pymysql.connect(host='192.168.243.2', port=3306, user='getter', passwd='123456', db='sdmo', charset='utf8')
        con3 = pymysql.connect(host='192.168.236.2', port=3306, user='getter', passwd='123456', db='sdmo', charset='utf8')
        con4 = pymysql.connect(host='192.168.128.2', port=3306, user='getter', passwd='123456', db='sdmo', charset='utf8')
    except:
        pass
    try:
        cur = con1.cursor()
        cur.execute("SELECT code,id FROM sdmo.stations")
        err_wells_server_all += update_well(cur.fetchall(), '192.168.241.2')
    except:
        err_sdmo_server.append('192.168.241.2')
    try:
        cur = con2.cursor()
        cur.execute("SELECT code,id  FROM sdmo.stations")
        err_wells_server_all += update_well(cur.fetchall(), '192.168.243.2')
    except:
        err_sdmo_server.append('192.168.243.2')
    try:
        cur = con3.cursor()
        cur.execute("SELECT code,id  FROM sdmo.stations")
        err_wells_server_all += update_well(cur.fetchall(), '192.168.236.2')
    except:
        err_sdmo_server.append('192.168.236.2')
    try:
        cur = con4.cursor()
        cur.execute("SELECT code,id  FROM sdmo.stations")
        err_wells_server_all += update_well(cur.fetchall(), '192.168.128.2')
    except:
        err_sdmo_server.append('192.168.128.2')
    return Response({
        "info": "SUCCESS",
        "err_wells": err_wells_server_all,
        "err_sdmo_servers": err_sdmo_server
    })


# 11:50 or 11:30
@api_view(['GET'])
def update_sum_well(request):     
    for field in models.Field.objects.all():
        try:
            sum_well_in_field = models.SumWellInField.objects.get(field=field, timestamp=timezone.now())
        except:
            sum_well_in_field = models.SumWellInField.objects.create(field=field, timestamp=timezone.now())
            well_matrix = models.WellMatrix.objects.filter(timestamp=timezone.now(), well__field=field,
                                                           well__has_isu=True).aggregate(
                Avg('filling'), Sum('fluid_agzu'), Sum('fluid_isu'),
                Sum('teh_rej_fluid'), Sum('teh_rej_oil'), Avg('teh_rej_water'))

            sum_well_in_field.filling = well_matrix["filling__avg"]
            if not sum_well_in_field.filling:
                sum_well_in_field.filling = 0
            sum_well_in_field.fluid_agzu = well_matrix["fluid_agzu__sum"]
            if not sum_well_in_field.fluid_agzu:
                sum_well_in_field.fluid_agzu = 0
            sum_well_in_field.fluid_isu = well_matrix["fluid_isu__sum"]
            if not sum_well_in_field.fluid_isu:
                sum_well_in_field.fluid_isu = 0
            sum_well_in_field.teh_rej_fluid = well_matrix["teh_rej_fluid__sum"]
            if not sum_well_in_field.teh_rej_fluid:
                sum_well_in_field.teh_rej_fluid = 0
            sum_well_in_field.teh_rej_oil = well_matrix["teh_rej_oil__sum"]
            if not sum_well_in_field.teh_rej_oil:
                sum_well_in_field.teh_rej_oil = 0
            sum_well_in_field.teh_rej_water = well_matrix["teh_rej_water__avg"]
            if not sum_well_in_field.teh_rej_water:
                sum_well_in_field.teh_rej_water = 0
            sum_well_in_field.save()
    return Response({
        "message": "OK!"
    })


@api_view(['GET'])
def update_field_matrix(request):
    for field in models.Field.objects.all():
        try:
            field_matrix = models.FieldMatrix.objects.get(field=field, timestamp=timezone.now())
        except:
            field_matrix = models.FieldMatrix.objects.create(field=field, timestamp=timezone.now())
            well_matrix = models.WellMatrix.objects.filter(timestamp=timezone.now(), well__field=field).aggregate(
                Avg('filling'), Sum('fluid_agzu'), Sum('fluid_isu'),
                Sum('teh_rej_fluid'), Sum('teh_rej_oil'), Avg('teh_rej_water'))

            field_matrix.filling = well_matrix["filling__avg"]
            if not field_matrix.filling:
                field_matrix.filling = 0
            field_matrix.fluid_agzu = well_matrix["fluid_agzu__sum"]
            if not field_matrix.fluid_agzu:
                field_matrix.fluid_agzu = 0
            field_matrix.fluid_isu = well_matrix["fluid_isu__sum"]
            if not field_matrix.fluid_isu:
                field_matrix.fluid_isu = 0
            field_matrix.teh_rej_fluid = well_matrix["teh_rej_fluid__sum"]
            if not field_matrix.teh_rej_fluid:
                field_matrix.teh_rej_fluid = 0
            field_matrix.teh_rej_oil = well_matrix["teh_rej_oil__sum"]
            if not field_matrix.teh_rej_oil:
                field_matrix.teh_rej_oil = 0
            field_matrix.teh_rej_water = well_matrix["teh_rej_water__avg"]
            if not field_matrix.teh_rej_water:
                field_matrix.teh_rej_water = 0
            field_matrix.save()
    return Response({
        "message": "OK!"
    })


@api_view(['GET'])
def update_matrix(request):
    wells = models.Well.objects.all()
    err_emgcm_data = list()
    err_sdmo_data = list()
    # err_sdmo_server_all = list()
    try:
        con1 = pymysql.connect(host='192.168.241.2', port=3306, user='getter', passwd='P@ssw0rD', db='sdmo', charset='utf8')
        con2 = pymysql.connect(host='192.168.243.2', port=3306, user='getter', passwd='123456', db='sdmo', charset='utf8')
        con3 = pymysql.connect(host='192.168.236.2', port=3306, user='getter', passwd='123456', db='sdmo', charset='utf8')
        con4 = pymysql.connect(host='192.168.128.2', port=3306, user='getter', passwd='123456', db='sdmo', charset='utf8')
    except:
        pass

    for well in wells:
        try:
            well_matrix = models.WellMatrix.objects.get(timestamp=timezone.now(), well=well)
        except:
            well_matrix = models.WellMatrix.objects.create(timestamp=timezone.now(), well=well)
        try: 
            conn = pymysql.connect(host='192.168.17.158', port=3306, user='root', passwd='1234', db='emg-cm',
                                   charset='utf8')
            cur = conn.cursor()
            cur.execute("SELECT zamer, tr_fluid, tr_oil, tr_water FROM n_well_matrix where well='" + well.name + "'")
            row_values = cur.fetchone()
            if (row_values[0] is not None) and (row_values[1] is not None) and (row_values[2] is not None) and (row_values[3] is not None):
                well_matrix.fluid_agzu = row_values[0]
                well_matrix.teh_rej_fluid = row_values[1]
                well_matrix.teh_rej_oil = row_values[2]
                well_matrix.teh_rej_water = row_values[3]
            else:
                well_matrix.fluid_agzu = 0
                well_matrix.teh_rej_fluid = 0
                well_matrix.teh_rej_oil = 0
                well_matrix.teh_rej_water = 0
                err_emgcm_data.append(well.name)
        except:
            err_emgcm_data.append(well.name)

        if well.server == "192.168.241.2":
            try:
                cur = con1.cursor()
                cur.execute("SELECT avg_1997, debit_theoretical, no_work FROM sdmo.daily_data where station_id='"+str(well.well_id)+"' order by day desc limit 1")
                row_values = cur.fetchone()

                if (row_values[0] is not None) and (row_values[1] is not None) and (row_values[2] is not None):
                    well_matrix.filling = row_values[0]
                    well_matrix.fluid_isu = row_values[1]
                    well.well_stop += row_values[2] / 60
                    well.shortage_isu += well.well_stop * well_matrix.teh_rej_oil / 24 / 60
 
                else:
                    err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                    well_matrix.filling = 0 
                    well_matrix.fluid_isu = 0
            except:
                err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                well_matrix.filling = 0
                well_matrix.fluid_isu = 0
        elif well.server == "192.168.243.2":
            try:
                cur = con2.cursor()
                cur.execute("SELECT avg_1997,debit_theoretical,no_work FROM sdmo.daily_data where station_id='"+str(well.well_id)+"' order by day desc limit 1")
                row_values = cur.fetchone()
                if (row_values[0] is not  None) and (row_values[1] is not None) and (row_values[2] is not None):
                    well_matrix.filling = row_values[0]
                    well_matrix.fluid_isu = row_values[1]
                    well.well_stop += row_values[2] / 60
                    well.shortage_isu += well.well_stop * well_matrix.teh_rej_oil / 24 / 60
 
                else:
                    err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                    well_matrix.filling = 0 
                    well_matrix.fluid_isu = 0
            except:
                err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                well_matrix.filling = 0
                well_matrix.fluid_isu = 0
        elif well.server == "192.168.236.2":
            try:
                cur = con3.cursor()
                cur.execute("SELECT avg_1997,debit_theoretical,no_work FROM sdmo.daily_data where station_id='"+str(well.well_id)+"' order by day desc limit 1")
                row_values = cur.fetchone()
                if (row_values[0] is not None) and (row_values[1] is not None) and (row_values[2] is not None):
                    well_matrix.filling = row_values[0]
                    well_matrix.fluid_isu = row_values[1]
                    well.well_stop += row_values[2] / 60
                    well.shortage_isu += well.well_stop * well_matrix.teh_rej_oil / 24 / 60
 
                else:
                    err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                    well_matrix.filling = 0 
                    well_matrix.fluid_isu = 0
            except:
                err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                well_matrix.filling = 0
                well_matrix.fluid_isu = 0
        elif well.server == "192.168.128.2":
            try:
                cur = con4.cursor()
                cur.execute("SELECT avg_1997,debit_theoretical,no_work FROM sdmo.daily_data where station_id='"+str(well.well_id)+"' order by day desc limit 1")
                row_values = cur.fetchone()
                if (row_values[0] is not None) and (row_values[1] is not None) and (row_values[2] is not None):
                    well_matrix.filling = row_values[0]
                    well_matrix.fluid_isu = row_values[1]
                    well.well_stop += row_values[2] / 60
                    well.shortage_isu += well.well_stop * well_matrix.teh_rej_oil / 24 / 60
 
                else:
                    err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                    well_matrix.filling = 0 
                    well_matrix.fluid_isu = 0
            except:
                err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                well_matrix.filling = 0
                well_matrix.fluid_isu = 0
        well_matrix.save()
        well.save()
    return Response({
        "info": "SUCCESS",
        "err_staition_teh_rej_null": err_emgcm_data,
        "err_sdmo_data":err_sdmo_data  
    })


@api_view(['GET'])
def update_events(request):
    filter_date = datetime(2021, 1, 1)
    con = cx_Oracle.connect('integration_EMG/integra@172.20.10.220/orcl', encoding='UTF-8', nencoding='UTF-8')
    cur = con.cursor()
    wells = models.Well.objects.filter(tbd_id__isnull=False)
    for well in wells:
        cur.execute("SELECT * FROM WELL_REPAIR_ACT_TRANSFER where WELL_ID=" + str(well.tbd_id)
                    + " and DBEG > to_date('2021-01-01', 'yyyy-MM-dd')")

        transfers = cur.fetchall()
        rem_count = 0
        well_stop = 0
        shortage_prs = 0
        end = datetime(2021, 1, 1)

        for transfer in transfers:
            rem_count += 1
            beg_id = transfer[0]
            beg = transfer[4]
            rem_name = transfer[5]
            if int(transfer[2] == 1):
                rem_type = 'КРС'
            elif int(transfer[2] == 2):
                rem_type = 'ТРС'
            elif int(transfer[2] == 3):
                rem_type = 'ПРС'
            else:
                rem_type = 'Прочие простои'

            cur.execute("SELECT * FROM WELL_REPAIR_ACT_RETURN where WELL_REPAIR_ACT_TRANSFER_ID=" + str(beg_id))
            act_return = cur.fetchone()
            if act_return:
                end = act_return[2]

            hours = 0
            if end.year > 2022:
                end = end.replace(year=2021)

            if end > beg:
                diff = end - beg
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600

            well_stop += hours / 24

            cur.execute("SELECT * FROM REPAIR_WORK_TYPE where ID=" + str(rem_name))
            work_type = cur.fetchone()
            if work_type:
                event = work_type[1]

            got, created = models.WellEvents.objects.get_or_create(well=well, event_type=rem_type, event=event,
                                                                   beg=beg)

            if beg <= end:
                daily_data = models.WellMatrix.objects.filter(well=well, timestamp__gte=beg, timestamp__lte=end)
                for daily_item in daily_data:
                    daily_item.fluid_agzu = 0
                    daily_item.park_fluid = 0
                    daily_item.save()

            if created:
                got.end = end
                got.save()
                cur.execute("SELECT * FROM TECH_MODE where WELL_ID=" + str(well.tbd_id)
                            + " and DBEG < to_date('" + beg.strftime('%Y-%m-%d') + "','yyyy-MM-dd')"
                            + " and DEND > to_date('" + beg.strftime('%Y-%m-%d') + "','yyyy-MM-dd')"
                            + " and DBEG > to_date('2021-01-01','yyyy-MM-dd')")
                oil = cur.fetchone()
                if oil:
                    shortage_prs += oil[6] * hours / 24

            if (not created) and (got.beg > got.end):
                got.end = end
                got.save()

            if (not created) and (got.beg <= got.end):
                cur.execute("SELECT * FROM TECH_MODE where WELL_ID=" + str(well.tbd_id)
                            + " and DBEG < to_date('" + beg.strftime('%Y-%m-%d') + "','yyyy-MM-dd')"
                            + " and DEND > to_date('" + beg.strftime('%Y-%m-%d') + "','yyyy-MM-dd')"
                            + " and DBEG > to_date('2021-01-01','yyyy-MM-dd')")
                oil = cur.fetchone()
                if oil:
                    shortage_prs += oil[6] * hours / 24

        cur.execute("SELECT * FROM GTM where WELL_ID=" + str(well.tbd_id)
                    + " and DBEG > to_date('2021-01-01', 'yyyy-MM-dd') and DEND > to_date('2021-01-01', 'yyyy-MM-dd')")

        transfers = cur.fetchall()

        for transfer in transfers:
            rem_count += 1
            rem_name = transfer[2]
            beg = transfer[3]
            end = transfer[4]
            rem_type = 'ГТМ'

            hours = 0
            if end.year > 2022:
                end = end.replace(year=2021)

            if end > beg:
                diff = end - beg
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600

            well_stop += hours / 24

            if rem_name:
                cur.execute("SELECT * FROM GTM_TYPE where ID=" + str(rem_name))
                work_type = cur.fetchone()
                if work_type:
                    event = work_type[1]
            else:
                event = '----'

            got, created = models.WellEvents.objects.get_or_create(well=well, event_type=rem_type, event=event,
                                                                   beg=beg)

            if beg <= end:
                daily_data = models.WellMatrix.objects.filter(well=well, timestamp__gte=beg, timestamp__lte=end)
                for daily_item in daily_data:
                    daily_item.fluid_agzu = 0
                    daily_item.park_fluid = 0
                    daily_item.save()

            if created:
                got.end = end
                got.save()
                cur.execute("SELECT * FROM TECH_MODE where WELL_ID=" + str(well.tbd_id)
                            + " and DBEG < to_date('" + beg.strftime('%Y-%m-%d') + "','yyyy-MM-dd')"
                            + " and DEND > to_date('" + beg.strftime('%Y-%m-%d') + "','yyyy-MM-dd')"
                            + " and DBEG > to_date('2021-01-01','yyyy-MM-dd')")
                oil = cur.fetchone()
                if oil:
                    shortage_prs += oil[6] * hours / 24

            if (not created) and (got.beg > got.end):
                got.end = end
                got.save()

            if (not created) and (got.beg <= got.end):
                cur.execute("SELECT * FROM TECH_MODE where WELL_ID=" + str(well.tbd_id)
                            + " and DBEG < to_date('" + beg.strftime('%Y-%m-%d') + "','yyyy-MM-dd')"
                            + " and DEND > to_date('" + beg.strftime('%Y-%m-%d') + "','yyyy-MM-dd')"
                            + " and DBEG > to_date('2021-01-01','yyyy-MM-dd')")
                oil = cur.fetchone()
                if oil:
                    shortage_prs += oil[6] * hours / 24

        well.rem_count = rem_count
        well.well_stop_prs = well_stop
        well.shortage_prs = shortage_prs
        well.save()

    con.close()
    prod = models.Constant.objects.get(name='Дополнительная добыча').max
    all_count = models.WellEvents.objects.filter(beg__gte=filter_date).count()
    for event in models.Events.objects.filter(field=None):
        count = models.WellEvents.objects.filter(beg__gte=filter_date, event=event.event).count()
        event.fact = count
        event.coef = count / all_count
        event.effect = prod * event.coef
        event.save()

    for field in models.Field.objects.all():
        for event in models.Events.objects.filter(field=field):
            count = models.WellEvents.objects.filter(beg__gte=filter_date, event=event.event, well__field=field).count()
            event.fact = count
            event.coef = count / all_count
            event.effect = prod * event.coef
            event.save()

    return Response({
        "info": "Данные загружены"
    })


@api_view(['GET'])
def update_prs(request):
    server = '192.168.17.110'
    database = 'toucan'
    username = 'sa'
    password = 'Sql**'
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database
                          + ';UID=' + username + ';PWD=' + password)
    tempDate = datetime.now().strftime('%Y-%m-%d')
    first = "select distinct DEVICEID from toucan.dbo.MEASURE where (ONDATETIME between '" \
            + tempDate + " 00:00:00' and '" + tempDate + " 23:59:59') order by DEVICEID"

    th = "select ONDATETIME, PVALUE from [toucan_export2].[dbo].[POINT] where ([ONDATETIME] between '" \
         + tempDate + " 00:00:00' and '" + tempDate + " 23:59:59') and (PID=512) and ([DEVICEID]="

    measure = "select * from [toucan_export2].[dbo].[MEASURE] where ([ONDATETIME] between '" \
              + tempDate + " 00:00:00' and '" + tempDate + " 23:59:59') and ([DEVICEID]="

    description = "select * from [toucan].[dbo].[DIRECTORY] where [NAME]="

    cursor = conn.cursor()
    cursor.execute(first)
    devices = cursor.fetchall()

    for item in devices:
        device = item[0]
        query = th + str(device) + ")"
        query2 = measure + str(device) + ")"
        q_desc = description + str(device)
        cursor.execute(query2)
        measures = cursor.fetchall()


    return Response({
        "info": "Данные загружены"
    })


@api_view(['GET'])
def update_kpn(request):
    wells = models.Well.objects.filter(has_isu=True)
    for well in wells:
        item = models.WellMatrix.objects.filter(well=well).order_by('-timestamp').first()
        teh = item.teh_rej_fluid
        if well.tpn != 1:
            teh = well.tpn
        isu = item.fluid_agzu
        if teh != 0 and isu != 0:
            kpn = isu / teh
            item.kpn = kpn
            item.save()
            if well.production_type == models.Well.SGN:
                kpn_constant = models.Constant.objects.get(name='КПН')
                time_threshold = datetime.now() - timedelta(days=365)
                has_event = models.WellEvents.objects.filter(well=well, event__contains='Смена насоса',
                                                             end__gt=time_threshold).exists()
                if kpn <= kpn_constant.max and not has_event:
                    models.Recommendation.objects.create(well=well, kpn=kpn, event='Проверить на предмет утечек')

    return Response({
        "info": "Данные обновлены"
    })


@api_view(['GET'])
def send_mails(request):
    mail_sender = smtplib.SMTP('smtp.gmail.com', 587)
    mail_sender.ehlo()
    mail_sender.starttls()
    mail_sender.ehlo()
    mail_sender.login("noreply@dlc.kz", "Xm*6%R7u")
    dt = datetime.today()
    well_perf_sets = models.MailSettings.objects.filter(type=models.MailSettings.well_perf)
    for sett in well_perf_sets:
        field = sett.field
        recs = models.Recommendation.objects.filter(well__field=field, timestamp=dt)
        wells = ''
        all_wells = ''

        for rec in recs:
            wells += rec.well.name + ': ' + str(round(rec.kpn, 2)) + '\n'

        all_recs_dt = models.WellMatrix.objects.filter(well__field=field).order_by('-id')[0].timestamp
        all_recs = models.WellMatrix.objects.filter(well__field=field, timestamp=all_recs_dt)
        kpn_constant = models.Constant.objects.get(name='КПН')

        for rec in all_recs:
            if rec.kpn <= kpn_constant.max:
                all_wells += rec.well.name + ': ' + str(round(rec.kpn, 2)) + '\n'

        mail_users = models.MailUser.objects.filter(mail=sett)
        for mail_user in mail_users:
            send_to = mail_user.email
            text = 'Уважаемый(ая) ' + mail_user.name + ', ' + '\n' \
                   + 'зафиксировано снижение производительности скважины.' + '\n' + '\n' \
                   + 'КПН по скважинам:' + '\n' + all_wells + '\n' \
                   + 'Из них, факт смены насоса был зафиксирован более года назад на:' + '\n' + wells + '\n' \
                   + 'С уважением, noreply@dlc.kz!'
            body = "\r\n".join((
                "From: %s" % 'noreply@dlc.kz',
                "To: %s" % send_to,
                "Subject: %s" % sett.body + ': ' + sett.type,
                "",
                text
            ))
            mail_sender.sendmail('noreply@dlc.kz', [send_to], body.encode('utf-8'))
        models.MailHistory.objects.create(mail=sett)

    return Response({
        "info": "Сообщения отправлены"
    })


@api_view(['GET'])
def update_watt(request):
    try:
        con1 = pymysql.connect(host='192.168.241.2', port=3306, user='getter', passwd='P@ssw0rD', db='sdmo', charset='utf8')
        # con2 = pymysql.connect(host='192.168.243.2', port=3306, user='getter', passwd='123456', db='sdmo', charset='utf8')
        # con3 = pymysql.connect(host='192.168.236.2', port=3306, user='getter', passwd='123456', db='sdmo', charset='utf8')
        # con4 = pymysql.connect(host='192.168.128.2', port=3306, user='getter', passwd='123456', db='sdmo', charset='utf8')
    except:
        pass
    wells = models.Well.objects.filter(has_isu=True, field__name='UAZ')
    for well in wells:
        if well.server == "192.168.241.2":
            try:
                cur = con1.cursor()
                cur.execute("SELECT date,time,value FROM sdmo.osc_data where reg=1610 and station_id='" + str(well.well_id) + "' order by date desc limit 1")
                row_values = cur.fetchone()
                t = (datetime.min + row_values[1]).time()
                dt = datetime.combine(row_values[0], t)
                arr = str(row_values[2]).split(',')

                try:
                    models.Wattmetrogram.objects.get(well=well, timestamp=dt)
                except:
                    models.Wattmetrogram.objects.create(well=well, x=[], y=arr, timestamp=dt)
            except:
                pass


    try:
        con1.close()
    except:
        pass

    return Response({
        "info": "SUCCESS"
    })


@api_view(['GET'])
def update_tbd_data(request):
    con = cx_Oracle.connect('integration_EMG/integra@172.20.10.220/orcl', encoding='UTF-8', nencoding='UTF-8')
    cur = con.cursor()
    wells = models.Well.objects.filter(tbd_id__isnull=False)

    for well in wells:
        try:
            cur.execute("SELECT WELL_STATUS_TYPE_ID FROM WELL_STATUS where WELL_ID=" + str(well.tbd_id)
                        + " and ROWNUM <= 1 order by DBEG desc")

            row_values = cur.fetchone()
            status_id = row_values[0]
            cur.execute("SELECT NAME_RU FROM WELL_STATUS_TYPE where ID=" + str(status_id))
            row_values = cur.fetchone()
            status = row_values[0]

            cur.execute("SELECT LIQUID_VAL FROM LIQUID_PROD where WELL_ID=" + str(well.tbd_id)
                        + " and ROWNUM <= 1 order by DBEG desc")
            row_values = cur.fetchone()
            tbd_fluid = row_values[0]

            cur.execute("SELECT VALUE_DOUBLE FROM CURRENT_GDIS_VALUE where WELL_ID=" + str(well.tbd_id)
                        + " and PARAM_GDIS_ID=211 and ROWNUM <= 1 order by DBEG desc")
            row_values = cur.fetchone()
            p_zab = row_values[0]

            cur.execute("SELECT VALUE_DOUBLE FROM CURRENT_GDIS_VALUE where WELL_ID=" + str(well.tbd_id)
                        + " and PARAM_GDIS_ID=210 and ROWNUM <= 1 order by DBEG desc")
            row_values = cur.fetchone()
            p_plast = row_values[0]

            cur.execute("SELECT VALUE_DOUBLE FROM CURRENT_GDIS_VALUE where WELL_ID=" + str(well.tbd_id)
                        + " and PARAM_GDIS_ID=217 and ROWNUM <= 1 order by DBEG desc")
            row_values = cur.fetchone()
            dyn_level = row_values[0]

            well_matrix = models.WellMatrix.objects.filter(well=well).order_by('-timestamp').first()
            well_matrix.tbd_fluid = tbd_fluid
            well_matrix.status = status
            well_matrix.p_plast = p_plast
            well_matrix.p_zab = p_zab
            well_matrix.dyn_level = dyn_level
            well_matrix.save()
        except:
            pass

    con.close()

    return Response({
        "info": "SUCCESS"
    })


@api_view(['GET'])
def update_sdmo_data(request):
    wells = models.Well.objects.filter(has_isu=True, server="192.168.241.2")
    try:
        con1 = pymysql.connect(host='192.168.241.2', port=3306, user='getter', passwd='P@ssw0rD', db='sdmo', charset='utf8')
    except Exception as e:
        pass
    try:
        con2 = pymysql.connect(host='192.168.243.2', port=3306, user='getter', passwd='123456', db='sdmo', charset='utf8')
    except Exception as e:
        pass
    try:
        con3 = pymysql.connect(host='192.168.236.2', port=3306, user='getter', passwd='123456', db='sdmo', charset='utf8')
    except Exception as e:
        pass
    try:
        con4 = pymysql.connect(host='192.168.128.2', port=3306, user='getter', passwd='123456', db='sdmo', charset='utf8')
    except Exception as e:
        pass

    for well in wells:
        try:
            if well.server == "192.168.241.2":
                cur = con1.cursor()
            if well.server == "192.168.243.2":
                cur = con2.cursor()
            if well.server == "192.168.236.2":
                cur = con3.cursor()
            if well.server == "192.168.128.2":
                cur = con4.cursor()

            cur.execute("SELECT value FROM fc_data_last where reg=1999 and station_id=" + str(well.well_id)
                        + " order by savetime desc")
            row_values = cur.fetchone()
            sdmo_status = float(row_values[0])
            cur.execute("SELECT value FROM fc_data_last where reg=1997 and station_id=" + str(well.well_id)
                        + " order by savetime desc")
            row_values = cur.fetchone()
            filling = float(row_values[0])
            cur.execute("SELECT value FROM fc_data_last where reg=1998 and station_id=" + str(well.well_id)
                        + " order by savetime desc")
            row_values = cur.fetchone()
            pump_speed = float(row_values[0])

            cur.execute("SELECT electric_cons, debit_theoretical FROM daily_data where station_id='" + str(well.well_id)
                        + "' order by day desc limit 1")
            row_values = cur.fetchone()
            electric_cons = float(row_values[0])
            fluid_isu = float(row_values[1])

            well_matrix = models.WellMatrix.objects.filter(well=well).order_by('-timestamp').first()
            well_matrix.sdmo_status = sdmo_status
            well_matrix.filling = filling
            well_matrix.fluid_isu = fluid_isu
            well_matrix.pump_speed = pump_speed
            well_matrix.electric_cons = electric_cons
            well_matrix.save()
        except:
            pass

    con1.close()

    return Response({
        "info": "SUCCESS"
    })

# for event in events:
#     ...:     field = event.well.field.name
#     ...:     well = event.well.name
#     ...:     start_date = event.beg.strftime("%Y-%m-%d %H:%M:%S")
#     ...:     end_date = event.end.strftime("%Y-%m-%d %H:%M:%S")
#     ...:     t = event.event_type
#     ...:     if event.event_type == WellEvents.GTM:
#     ...:         t = 'gtm'
#     ...:     work = event.event
#     ...:     cur.execute("insert into n_last10 (oil_field, well, start_date, end_date, type, work, foreign_id) values ('"+field+"','"+w
#     ...: ell+"','"+start_date+"','"+end_date+"','"+t+"','"+work+"',0)")