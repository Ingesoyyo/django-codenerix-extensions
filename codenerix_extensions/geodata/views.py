# -*- coding: utf-8 -*-
#
# django-codenerix-extensions
#
# Copyright 2017 Centrologic Computational Logistic Center S.L.
#
# Project URL : http://www.codenerix.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ast
import operator

from django.db.models import Q
from django.conf import settings

from django.utils.translation import ugettext as _

from codenerix.multiforms import MultiForm
from codenerix.views import GenList, GenCreate, GenCreateModal, GenUpdate, GenUpdateModal, GenDelete, GenForeignKey

from .models import Continent, Country, Region, Province, TimeZone, City, MODELS
from .forms import ContinentForm, CountryForm, RegionForm, ProvinceForm, TimeZoneForm, CityForm


# forms for multiforms
formsfull = {}

for info in MODELS:
    field = info[0]
    model = info[1]
    formsfull[model] = [(None, None, None)]
    for lang_code in settings.LANGUAGES_DATABASES:
        query = 'from .models import {}GeoName{}\n'.format(model, lang_code)
        query += 'from .forms import {}TextForm{}'.format(model, lang_code)
        exec(query)

        formsfull[model].append((eval('{}TextForm{}'.format(model, lang_code.upper())), field, None))


class TranslatedMixin(object):

    @property
    def lang(self):
        for x in settings.LANGUAGES:
            if x[0] == self.request.LANGUAGE_CODE:
                return self.request.LANGUAGE_CODE.lower()
        return settings.LANGUAGES[0][0].lower()


# ###########################################
# Continent
class GenContinentUrl(object):
    ws_entry_point = '{}/continents'.format(settings.CDNX_GEODATA_URL)


class ContinentList(TranslatedMixin, GenContinentUrl, GenList):
    model = Continent
    linkadd = False
    show_details = False
    public = True

    def __fields__(self, info):
        return [
            ('name:{}__name'.format(self.lang), _('Name')),
        ]

    def dispatch(self, request, *args, **kwargs):
        self.order_by = ['{}__name'.format(self.lang)]
        return super(ContinentList, self).dispatch(request, *args, **kwargs)


class ContinentCreate(GenContinentUrl, MultiForm, GenCreate):
    model = Continent
    form_class = ContinentForm
    forms = formsfull['Continent']


class ContinentCreateModal(GenCreateModal, ContinentCreate):
    pass


class ContinentUpdate(GenContinentUrl, MultiForm, GenUpdate):
    model = Continent
    form_class = ContinentForm
    forms = formsfull['Continent']


class ContinentUpdateModal(GenUpdateModal, ContinentUpdate):
    pass


class ContinentDelete(GenContinentUrl, GenDelete):
    model = Continent


# ###########################################
# Country
class GenCountryUrl(object):
    ws_entry_point = '{}/countries'.format(settings.CDNX_GEODATA_URL)


class CountryList(TranslatedMixin, GenCountryUrl, GenList):
    model = Country
    linkadd = False
    show_details = False
    public = True

    def __limitQ__(self, info):
        result = {}
        try:
            params = ast.literal_eval(info.request.GET.get('json'))
        except ValueError:
            params = []
        if 'continent' in params:
            result['continent_limit'] = Q(continent__pk=int(params['continent']))
        return result

    def __fields__(self, info):
        return [
            ('code', _('Code')),
            ('name:{}__name'.format(self.lang), _('Name')),
        ]

    def dispatch(self, request, *args, **kwargs):
        self.order_by = ['{}__name'.format(self.lang)]
        return super(CountryList, self).dispatch(request, *args, **kwargs)


class CountryCreate(GenCountryUrl, MultiForm, GenCreate):
    model = Country
    form_class = CountryForm
    forms = formsfull['Country']


class CountryCreateModal(GenCreateModal, CountryCreate):
    pass


class CountryUpdate(GenCountryUrl, MultiForm, GenUpdate):
    model = Country
    form_class = CountryForm
    forms = formsfull['Country']


class CountryUpdateModal(GenUpdateModal, CountryUpdate):
    pass


class CountryDelete(GenCountryUrl, GenDelete):
    model = Country


class CountryForeign(GenCountryUrl, GenForeignKey):
    model = Country
    label = "{<LANGUAGE_CODE>__name}"

    def get_foreign(self, queryset, search, filters):
        # Filter with search string
        qsobject = Q(code__icontains=search)

        for lang in settings.LANGUAGES_DATABASES:
            qsobject |= Q(**{"{}__name__icontains".format(lang.lower()): search})
        qs = queryset.filter(qsobject)
        return qs[:settings.LIMIT_FOREIGNKEY]


# ###########################################
# Regions
class GenRegionUrl(object):
    ws_entry_point = '{}/regions'.format(settings.CDNX_GEODATA_URL)


class RegionList(TranslatedMixin, GenRegionUrl, GenList):
    model = Region
    linkadd = False
    show_details = False
    public = True

    def __limitQ__(self, info):
        result = {}
        try:
            params = ast.literal_eval(info.request.GET.get('json'))
        except ValueError:
            params = []
        if 'continent' in params:
            result['continent_limit'] = Q(country__continent__pk=int(params['continent']))
        if 'country' in params:
            result['country_limit'] = Q(country__pk=int(params['country']))
        return result

    def __fields__(self, info):
        return [
            ('name:{}__name'.format(self.lang), _('Name')),
        ]

    def dispatch(self, request, *args, **kwargs):
        self.order_by = ['{}__name'.format(self.lang)]
        return super(RegionList, self).dispatch(request, *args, **kwargs)


class RegionCreate(GenRegionUrl, MultiForm, GenCreate):
    model = Region
    form_class = RegionForm
    forms = formsfull['Region']


class RegionCreateModal(GenCreateModal, RegionCreate):
    pass


class RegionUpdate(GenRegionUrl, MultiForm, GenUpdate):
    model = Region
    form_class = RegionForm
    forms = formsfull['Region']


class RegionUpdateModal(GenUpdateModal, RegionUpdate):
    pass


class RegionDelete(GenRegionUrl, GenDelete):
    model = Region


class RegionForeign(GenRegionUrl, GenForeignKey):
    model = Region
    label = "{<LANGUAGE_CODE>__name}"

    def get_foreign(self, queryset, search, filters):
        # Filter with search string
        qsobject = Q(code__icontains=search)

        for lang in settings.LANGUAGES_DATABASES:
            qsobject |= Q(**{"{}__name__icontains".format(lang.lower()): search})
        qs = queryset.filter(qsobject)

        country = filters.get('country', None)
        if country:
            qs = qs.filter(country__pk=country)
        return qs[:settings.LIMIT_FOREIGNKEY]


# ###########################################
# Provinces
class GenProvinceUrl(object):
    ws_entry_point = '{}/provinces'.format(settings.CDNX_GEODATA_URL)


class ProvinceList(TranslatedMixin, GenProvinceUrl, GenList):
    model = Province
    linkadd = False
    show_details = False
    public = True

    def __limitQ__(self, info):
        result = {}
        try:
            params = ast.literal_eval(info.request.GET.get('json'))
        except ValueError:
            params = []
        if 'continent' in params:
            result['continent_limit'] = Q(region__country__continent__pk=int(params['continent']))
        if 'country' in params:
            result['country_limit'] = Q(region__country__pk=int(params['country']))
        if 'region' in params:
            result['region_limit'] = Q(region__pk=int(params['region']))
        return result

    def __fields__(self, info):
        return [
            ('name:{}__name'.format(self.lang), _('Name')),
        ]

    def dispatch(self, request, *args, **kwargs):
        self.order_by = ['{}__name'.format(self.lang)]
        return super(ProvinceList, self).dispatch(request, *args, **kwargs)


class ProvinceCreate(GenProvinceUrl, MultiForm, GenCreate):
    model = Province
    form_class = ProvinceForm
    forms = formsfull['Province']


class ProvinceCreateModal(GenCreateModal, ProvinceCreate):
    pass


class ProvinceUpdate(GenProvinceUrl, MultiForm, GenUpdate):
    model = Province
    form_class = ProvinceForm
    forms = formsfull['Province']


class ProvinceUpdateModal(GenUpdateModal, ProvinceUpdate):
    pass


class ProvinceDelete(GenProvinceUrl, GenDelete):
    model = Province


class ProvinceForeign(GenProvinceUrl, GenForeignKey):
    model = Province
    label = "{<LANGUAGE_CODE>__name}"

    def get_foreign(self, queryset, search, filters):
        # Filter with search string
        qsobject = Q(code__icontains=search)

        for lang in settings.LANGUAGES_DATABASES:
            qsobject |= Q(**{"{}__name__icontains".format(lang.lower()): search})
        qs = queryset.filter(qsobject)

        region = filters.get('region', None)
        if region:
            qs = qs.filter(region__pk=region)
        return qs[:settings.LIMIT_FOREIGNKEY]


# ###########################################
# TimeZone
class GenTimeZoneUrl(object):
    ws_entry_point = '{}/timezones'.format(settings.CDNX_GEODATA_URL)


class TimeZoneList(GenTimeZoneUrl, GenList):
    model = TimeZone
    linkadd = False
    show_details = False
    public = True

    def dispatch(self, request, *args, **kwargs):
        self.order_by = ['name']
        return super(TimeZoneList, self).dispatch(request, *args, **kwargs)


class TimeZoneCreate(GenTimeZoneUrl, GenCreate):
    model = TimeZone
    form_class = TimeZoneForm


class TimeZoneCreateModal(GenCreateModal, TimeZoneCreate):
    pass


class TimeZoneUpdate(GenTimeZoneUrl, GenUpdate):
    model = TimeZone
    form_class = TimeZoneForm


class TimeZoneUpdateModal(GenUpdateModal, TimeZoneUpdate):
    pass


class TimeZoneDelete(GenTimeZoneUrl, GenDelete):
    model = TimeZone


# ###########################################
# City
class GenCityUrl(object):
    ws_entry_point = '{}/cities'.format(settings.CDNX_GEODATA_URL)


class CityList(TranslatedMixin, GenCityUrl, GenList):
    model = City
    linkadd = False
    show_details = False
    public = True

    def __limitQ__(self, info):
        result = {}
        try:
            params = ast.literal_eval(info.request.GET.get('json'))
        except ValueError:
            params = []
        if 'continent' in params:
            result['continent_limit'] = Q(region__country__continent__pk=int(params['continent']))
        if 'country' in params:
            result['country_limit'] = Q(country__pk=int(params['country']))
        if 'region' in params:
            result['region_limit'] = Q(region__pk=int(params['region']))
        if 'province' in params:
            result['province_limit'] = Q(province__pk=int(params['province']))
        if 'time_zone' in params:
            result['time_zone_limit'] = Q(time_zone__pk=int(params['time_zone']))
        return result

    def __fields__(self, info):
        return [
            ('name:{}__name'.format(self.lang), _('Name')),
        ]

    def dispatch(self, request, *args, **kwargs):
        self.order_by = ['{}__name'.format(self.lang)]
        return super(CityList, self).dispatch(request, *args, **kwargs)


class CityCreate(GenCityUrl, MultiForm, GenCreate):
    model = City
    form_class = CityForm
    forms = formsfull['City']


class CityCreateModal(GenCreateModal, CityCreate):
    pass


class CityUpdate(GenCityUrl, MultiForm, GenUpdate):
    model = City
    form_class = CityForm
    forms = formsfull['City']


class CityUpdateModal(GenUpdateModal, CityUpdate):
    pass


class CityDelete(GenCityUrl, GenDelete):
    model = City


class CityForeign(GenCityUrl, GenForeignKey):
    model = City
    label = "{<LANGUAGE_CODE>__name}"

    def get_foreign(self, queryset, search, filters):
        # Filter with search string
        qsobject = []
        for lang in settings.LANGUAGES_DATABASES:
            qsobject.append(Q(**{"{}__name__icontains".format(lang.lower()): search}))
        qs = queryset.filter(
            reduce(operator.or_, qsobject)
        )
        # qs = queryset.filter(qsobject)

        country = filters.get('country', None)
        if country:
            qs = qs.filter(country__pk=country)

        province = filters.get('province', None)
        if province:
            qs = qs.filter(province__pk=province)

        region = filters.get('region', None)
        if region:
            qs = qs.filter(region__pk=region)
        return qs[:settings.LIMIT_FOREIGNKEY]
