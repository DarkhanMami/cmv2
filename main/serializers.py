from django.db.models import QuerySet
from rest_framework import serializers

from api.serializers import UserSerializer
from main.models import *


class EmptySerializer(serializers.Serializer):
    pass


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ['name']


class WellSerializer(serializers.ModelSerializer):
    field = FieldSerializer(many=False, read_only=True)

    class Meta:
        model = Well
        fields = ['name', 'field', 'teh_rej_fluid', 'teh_rej_oil', 'teh_rej_water', 'production_type']


class WellMatrixSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = WellMatrix
        fields = ['well', 'filling', 'fluid_agzu', 'fluid_isu', 'shortage_isu', 'shortage_prs', 'shortage_wait',
                    'well_stop', 'oil_loss', 'active', 'has_isu', 'performance', 'brigade_num', 'ts_num']


class DepressionSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = Depression
        fields = ['well', 'densityPL', 'densityZB', 'densityDiff', 'fluid_av', 'timestamp']


class WellMatrixCreateSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = WellMatrix
        fields = ['well', ]


class FieldBalanceSerializer(serializers.ModelSerializer):
    field = FieldSerializer(many=False, read_only=True)

    class Meta:
        model = FieldBalance
        fields = ['field', 'transport_balance', 'ansagan_balance', 'transport_brutto', 'ansagan_brutto',
                  'transport_netto', 'ansagan_netto', 'transport_density', 'ansagan_density',
                  'agzu_fluid', 'agzu_oil', 'teh_rej_fluid', 'teh_rej_oil', 'timestamp']


class FieldBalanceCreateSerializer(serializers.ModelSerializer):
    field = FieldSerializer(many=False, read_only=True)

    class Meta:
        model = FieldBalance
        fields = ['field', 'transport_balance', 'transport_brutto', 'transport_netto', 'transport_density']


class TSSerializer(serializers.ModelSerializer):

    class Meta:
        model = TS
        fields = ['gos_num', 'marka', 'type', 'total_days', 'in_work', 'in_rem', 'day_off',
                  'month', 'year', 'field', 'kip', 'ktg']