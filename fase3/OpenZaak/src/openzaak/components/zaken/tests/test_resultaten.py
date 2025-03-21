# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2019 - 2020 Dimpact
from django.test import override_settings, tag

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import get_validation_errors, reverse
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openzaak.tests.utils import JWTAuthMixin, mock_ztc_oas_get

from .factories import ResultaatFactory, ZaakFactory
from .utils import get_operation_url, get_resultaattype_response, get_zaaktype_response


@tag("external-urls")
@override_settings(ALLOWED_HOSTS=["testserver"])
class ResultaatCreateExternalURLsTests(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True
    list_url = get_operation_url("resultaat_create")

    def test_create_external_resultaattype(self):
        catalogus = "https://externe.catalogus.nl/api/v1/catalogussen/1c8e36be-338c-4c07-ac5e-1adf55bec04a"
        zaaktype = "https://externe.catalogus.nl/api/v1/zaaktypen/b71f72ef-198d-44d8-af64-ae1932df830a"
        resultaattype = "https://externe.catalogus.nl/api/v1/resultaten/7a3e4a22-d789-4381-939b-401dbce29426"

        zaak = ZaakFactory(zaaktype=zaaktype)
        zaak_url = reverse(zaak)

        with requests_mock.Mocker() as m:
            mock_ztc_oas_get(m)
            m.get(zaaktype, json=get_zaaktype_response(catalogus, zaaktype))
            m.get(
                resultaattype, json=get_resultaattype_response(resultaattype, zaaktype)
            )

            response = self.client.post(
                self.list_url,
                {
                    "zaak": f"http://testserver{zaak_url}",
                    "resultaattype": resultaattype,
                    "toelichting": "some desc",
                },
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_create_external_resultaattype_fail_bad_url(self):
        zaak = ZaakFactory()
        zaak_url = reverse(zaak)

        response = self.client.post(
            self.list_url,
            {
                "zaak": f"http://testserver{zaak_url}",
                "resultaattype": "abcd",
                "toelichting": "some desc",
            },
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

        error = get_validation_errors(response, "resultaattype")
        self.assertEqual(error["code"], "bad-url")

    def test_create_external_resultaattype_fail_not_json_url(self):
        zaak = ZaakFactory()
        zaak_url = reverse(zaak)

        ServiceFactory.create(
            api_root="http://example.com/",
            api_type=APITypes.ztc,
        )

        with requests_mock.Mocker() as m:
            m.get("http://example.com/", status_code=200, text="<html></html>")

            response = self.client.post(
                self.list_url,
                {
                    "zaak": f"http://testserver{zaak_url}",
                    "resultaattype": "http://example.com/",
                    "toelichting": "some desc",
                },
            )

        error = get_validation_errors(response, "resultaattype")
        self.assertEqual(error["code"], "invalid-resource")

    def test_create_external_resultaattype_fail_invalid_schema(self):
        catalogus = "https://externe.catalogus.nl/api/v1/catalogussen/1c8e36be-338c-4c07-ac5e-1adf55bec04a"
        zaaktype = "https://externe.catalogus.nl/api/v1/zaaktypen/b71f72ef-198d-44d8-af64-ae1932df830a"
        resultaattype = "https://externe.catalogus.nl/api/v1/resultaten/7a3e4a22-d789-4381-939b-401dbce29426"

        zaak = ZaakFactory(zaaktype=zaaktype)
        zaak_url = reverse(zaak)

        with requests_mock.Mocker() as m:
            mock_ztc_oas_get(m)
            m.get(zaaktype, json=get_zaaktype_response(catalogus, zaaktype))
            m.get(
                resultaattype,
                json={
                    "url": resultaattype,
                    "zaaktype": zaaktype,
                    "archiefnominatie": "vernietigen",
                    "archiefactietermijn": "P10Y",
                },
            )

            response = self.client.post(
                self.list_url,
                {
                    "zaak": f"http://testserver{zaak_url}",
                    "resultaattype": resultaattype,
                    "toelichting": "some desc",
                },
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "resultaattype")
        self.assertEqual(error["code"], "invalid-resource")

    def test_create_external_resultaattype_fail_zaaktype_mismatch(self):
        catalogus = "https://externe.catalogus.nl/api/v1/catalogussen/1c8e36be-338c-4c07-ac5e-1adf55bec04a"
        zaaktype1 = "https://externe.catalogus.nl/api/v1/zaaktypen/b71f72ef-198d-44d8-af64-ae1932df830a"
        zaaktype2 = "https://externe.catalogus.nl/api/v1/zaaktypen/b923543f-97aa-4a55-8c20-889b5906cf75"
        resultaattype = "https://externe.catalogus.nl/api/v1/resultaten/7a3e4a22-d789-4381-939b-401dbce29426"

        zaak = ZaakFactory(zaaktype=zaaktype1)
        zaak_url = reverse(zaak)

        with requests_mock.Mocker() as m:
            mock_ztc_oas_get(m)
            m.get(zaaktype1, json=get_zaaktype_response(catalogus, zaaktype1))
            m.get(zaaktype2, json=get_zaaktype_response(catalogus, zaaktype2))
            m.get(
                resultaattype, json=get_resultaattype_response(resultaattype, zaaktype2)
            )

            response = self.client.post(
                self.list_url,
                {
                    "zaak": f"http://testserver{zaak_url}",
                    "resultaattype": resultaattype,
                    "toelichting": "some desc",
                },
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "zaaktype-mismatch")

    def test_create_external_resultaattype_fail_unknown_resource(self):
        zaak = ZaakFactory()
        zaak_url = reverse(zaak)

        response = self.client.post(
            self.list_url,
            {
                "zaak": f"http://testserver{zaak_url}",
                "resultaattype": "https://other-externe.catalogus.nl/api/v1/resultaattypen/1",
                "toelichting": "some desc",
            },
        )

        error = get_validation_errors(response, "resultaattype")
        self.assertEqual(error["code"], "unknown-service")

    def test_pagination_pagesize_param(self):
        ResultaatFactory.create_batch(10)

        response = self.client.get(self.list_url, {"pageSize": 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"], 10)
        self.assertEqual(
            data["next"], f"http://testserver{self.list_url}?page=2&pageSize=5"
        )
