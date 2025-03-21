from pathlib import Path

from django.test import TestCase, tag
from django.utils.translation import gettext as _

import requests_mock
from requests import RequestException
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from zgw_consumers.constants import AuthTypes
from zgw_consumers.test.factories import ServiceFactory

from openforms.api.exceptions import ServiceUnavailable
from openforms.formio.constants import DataSrcOptions
from openforms.formio.registry import register
from openforms.formio.typing import (
    RadioComponent,
    SelectBoxesComponent,
    SelectComponent,
)
from openforms.forms.tests.factories import FormFactory
from openforms.logging.models import TimelineLogProxy
from openforms.submissions.tests.factories import SubmissionFactory
from openforms.submissions.tests.mixins import SubmissionsMixin
from openforms.utils.tests.cache import clear_caches
from openforms.utils.tests.vcr import OFVCRMixin

TESTS_DIR = Path(__file__).parent.resolve()
TEST_FILES = TESTS_DIR / "files"


@tag("gh-4993")
class SelectReferentielijstenOptionsTests(OFVCRMixin, TestCase):
    VCR_TEST_FILES = TEST_FILES

    def setUp(self):
        super().setUp()

        # The requests to Referentielijsten are cached, we need to make sure
        # that the cache is reset between tests to correctly test different scenarios
        self.addCleanup(clear_caches)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.service = ServiceFactory.create(
            api_root="http://localhost:8004/api/v1/",
            slug="referentielijsten",
            auth_type=AuthTypes.no_auth,
        )
        cls.submission = SubmissionFactory.create()

    def test_success(self):
        component: SelectComponent = {
            "key": "select",
            "type": "select",
            "label": "Select",
            "data": {},
            "dataType": "string",
            "openForms": {
                "code": "tabel1",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        register.update_config(component, submission=self.submission, data={})

        self.assertEqual(
            component["data"].get("values"),
            [
                {"label": "Option 1", "value": "option1"},
                {"label": "Option 2", "value": "option2"},
            ],
        )

    def test_table_with_paginated_items(self):
        component: SelectComponent = {
            "key": "select",
            "type": "select",
            "label": "Select",
            "data": {},
            "dataType": "string",
            "openForms": {
                "code": "tabel-with-many-items",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        register.update_config(component, submission=self.submission, data={})

        self.assertEqual(
            component["data"].get("values"),
            [{"label": str(i), "value": str(i)} for i in range(101)],
        )

    def test_no_service_configured(self):
        component: SelectComponent = {
            "key": "select",
            "type": "select",
            "label": "Select",
            "data": {},
            "dataType": "string",
            "openForms": {
                "code": "tabel1",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": "",
                "translations": {},
            },
        }

        with self.assertRaises(ServiceUnavailable):
            register.update_config(component, submission=self.submission, data={})

        self.assertNotIn("values", component["data"])
        log = TimelineLogProxy.objects.for_object(self.submission.form).get()
        assert log.extra_data
        self.assertEqual(log.template, "logging/events/form_configuration_error.txt")
        self.assertEqual(
            log.extra_data["error"],
            _(
                "Cannot fetch from Referentielijsten API, because no `service` is configured."
            ),
        )

    def test_no_code_configured(self):
        component: SelectComponent = {
            "key": "select",
            "type": "select",
            "label": "Select",
            "data": {},
            "dataType": "string",
            "openForms": {
                "code": "",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        with self.assertRaises(ServiceUnavailable):
            register.update_config(component, submission=self.submission, data={})

        self.assertNotIn("values", component["data"])
        log = TimelineLogProxy.objects.for_object(self.submission.form).get()
        assert log.extra_data
        self.assertEqual(log.template, "logging/events/form_configuration_error.txt")
        self.assertEqual(
            log.extra_data["error"],
            _(
                "Cannot fetch from Referentielijsten API, because no `code` is configured."
            ),
        )

    def test_service_does_not_exist(self):
        component: SelectComponent = {
            "key": "select",
            "type": "select",
            "label": "Select",
            "data": {},
            "dataType": "string",
            "openForms": {
                "code": "tabel1",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        self.service.delete()

        with self.assertRaises(ServiceUnavailable):
            register.update_config(component, submission=self.submission, data={})

        self.assertNotIn("values", component["data"])
        log = TimelineLogProxy.objects.for_object(self.submission.form).get()
        assert log.extra_data
        self.assertEqual(log.template, "logging/events/form_configuration_error.txt")
        self.assertEqual(
            log.extra_data["error"],
            _(
                "Cannot fetch from Referentielijsten API, service with {service_slug} does not exist."
            ).format(service_slug=self.service.slug),
        )

    def test_items_not_found(self):
        component: SelectComponent = {
            "key": "select",
            "type": "select",
            "label": "Select",
            "data": {},
            "dataType": "string",
            "openForms": {
                "code": "non-existent",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        with self.assertRaises(ServiceUnavailable):
            register.update_config(component, submission=self.submission, data={})

        self.assertNotIn("values", component["data"])
        log = TimelineLogProxy.objects.for_object(self.submission.form).get()
        assert log.extra_data
        self.assertEqual(
            log.template, "logging/events/referentielijsten_failure_response.txt"
        )
        self.assertEqual(
            log.extra_data["error"],
            _("No results found from Referentielijsten API."),
        )

    @requests_mock.Mocker()
    def test_request_exception(self, m):
        component: SelectComponent = {
            "key": "select",
            "type": "select",
            "label": "Select",
            "data": {},
            "dataType": "string",
            "openForms": {
                "code": "tabel1",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        m.get(
            f"{self.service.api_root}items?tabel__code=tabel1",
            exc=RequestException("something went wrong"),
        )

        with self.assertRaises(ServiceUnavailable):
            register.update_config(component, submission=self.submission, data={})

        self.assertNotIn("values", component["data"])
        log = TimelineLogProxy.objects.for_object(self.submission.form).get()
        assert log.extra_data
        self.assertEqual(
            log.template, "logging/events/referentielijsten_failure_response.txt"
        )
        self.assertEqual(
            log.extra_data["error"],
            _(
                "Exception occurred while fetching from Referentielijsten API: something went wrong."
            ),
        )


@tag("gh-4993")
class SelectboxesReferentielijstenOptionsTests(OFVCRMixin, TestCase):
    VCR_TEST_FILES = TEST_FILES

    def setUp(self):
        super().setUp()

        # The requests to Referentielijsten are cached, we need to make sure
        # that the cache is reset between tests to correctly test different scenarios
        self.addCleanup(clear_caches)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.service = ServiceFactory.create(
            api_root="http://localhost:8004/api/v1/",
            slug="referentielijsten",
            auth_type=AuthTypes.no_auth,
        )
        cls.submission = SubmissionFactory.create()

    def test_success(self):
        component: SelectBoxesComponent = {
            "key": "selectboxes",
            "type": "selectboxes",
            "label": "Selectboxes",
            "values": [],
            "dataType": "string",
            "openForms": {
                "code": "tabel1",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        register.update_config(component, submission=self.submission, data={})

        self.assertEqual(
            component["values"],
            [
                {"label": "Option 1", "value": "option1"},
                {"label": "Option 2", "value": "option2"},
            ],
        )

    def test_no_service_configured(self):
        component: SelectBoxesComponent = {
            "key": "selectboxes",
            "type": "selectboxes",
            "label": "Selectboxes",
            "values": [],
            "dataType": "string",
            "openForms": {
                "code": "tabel1",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": "",
                "translations": {},
            },
        }

        with self.assertRaises(ServiceUnavailable):
            register.update_config(component, submission=self.submission, data={})

        self.assertEqual(component["values"], [])

        log = TimelineLogProxy.objects.for_object(self.submission.form).get()
        assert log.extra_data
        self.assertEqual(log.template, "logging/events/form_configuration_error.txt")
        self.assertEqual(
            log.extra_data["error"],
            _(
                "Cannot fetch from Referentielijsten API, because no `service` is configured."
            ),
        )

    def test_no_code_configured(self):
        component: SelectBoxesComponent = {
            "key": "selectboxes",
            "type": "selectboxes",
            "label": "Selectboxes",
            "values": [],
            "dataType": "string",
            "openForms": {
                "code": "",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        with self.assertRaises(ServiceUnavailable):
            register.update_config(component, submission=self.submission, data={})

        self.assertEqual(component["values"], [])

        log = TimelineLogProxy.objects.for_object(self.submission.form).get()
        assert log.extra_data
        self.assertEqual(log.template, "logging/events/form_configuration_error.txt")
        self.assertEqual(
            log.extra_data["error"],
            _(
                "Cannot fetch from Referentielijsten API, because no `code` is configured."
            ),
        )

    def test_service_does_not_exist(self):
        component: SelectBoxesComponent = {
            "key": "selectboxes",
            "type": "selectboxes",
            "label": "Selectboxes",
            "values": [],
            "dataType": "string",
            "openForms": {
                "code": "tabel1",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        self.service.delete()

        with self.assertRaises(ServiceUnavailable):
            register.update_config(component, submission=self.submission, data={})

        self.assertEqual(component["values"], [])

        log = TimelineLogProxy.objects.for_object(self.submission.form).get()
        assert log.extra_data
        self.assertEqual(log.template, "logging/events/form_configuration_error.txt")
        self.assertEqual(
            log.extra_data["error"],
            _(
                "Cannot fetch from Referentielijsten API, service with {service_slug} does not exist."
            ).format(service_slug=self.service.slug),
        )

    def test_items_not_found(self):
        component: SelectBoxesComponent = {
            "key": "selectboxes",
            "type": "selectboxes",
            "label": "Selectboxes",
            "values": [],
            "dataType": "string",
            "openForms": {
                "code": "non-existent",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        with self.assertRaises(ServiceUnavailable):
            register.update_config(component, submission=self.submission, data={})

        self.assertEqual(component["values"], [])

        log = TimelineLogProxy.objects.for_object(self.submission.form).get()
        assert log.extra_data
        self.assertEqual(
            log.template, "logging/events/referentielijsten_failure_response.txt"
        )
        self.assertEqual(
            log.extra_data["error"],
            _("No results found from Referentielijsten API."),
        )

    @requests_mock.Mocker()
    def test_request_exception(self, m):
        component: SelectBoxesComponent = {
            "key": "selectboxes",
            "type": "selectboxes",
            "label": "Selectboxes",
            "values": [],
            "dataType": "string",
            "openForms": {
                "code": "tabel1",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        m.get(
            f"{self.service.api_root}items?tabel__code=tabel1",
            exc=RequestException("something went wrong"),
        )

        with self.assertRaises(ServiceUnavailable):
            register.update_config(component, submission=self.submission, data={})

        self.assertEqual(component["values"], [])

        log = TimelineLogProxy.objects.for_object(self.submission.form).get()
        assert log.extra_data
        self.assertEqual(
            log.template, "logging/events/referentielijsten_failure_response.txt"
        )
        self.assertEqual(
            log.extra_data["error"],
            _(
                "Exception occurred while fetching from Referentielijsten API: something went wrong."
            ),
        )


@tag("gh-4993")
class RadioReferentielijstenOptionsTests(OFVCRMixin, TestCase):
    VCR_TEST_FILES = TEST_FILES

    def setUp(self):
        super().setUp()

        # The requests to Referentielijsten are cached, we need to make sure
        # that the cache is reset between tests to correctly test different scenarios
        self.addCleanup(clear_caches)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.service = ServiceFactory.create(
            api_root="http://localhost:8004/api/v1/",
            slug="referentielijsten",
            auth_type=AuthTypes.no_auth,
        )
        cls.submission = SubmissionFactory.create()

    def test_success(self):
        component: RadioComponent = {
            "key": "radio",
            "type": "radio",
            "label": "Radio",
            "values": [],
            "dataType": "string",
            "openForms": {
                "code": "tabel1",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        register.update_config(component, submission=self.submission, data={})

        self.assertEqual(
            component["values"],
            [
                {"label": "Option 1", "value": "option1"},
                {"label": "Option 2", "value": "option2"},
            ],
        )

    def test_no_service_configured(self):
        component: RadioComponent = {
            "key": "radio",
            "type": "radio",
            "label": "Radio",
            "values": [],
            "dataType": "string",
            "openForms": {
                "code": "tabel1",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": "",
                "translations": {},
            },
        }

        with self.assertRaises(ServiceUnavailable):
            register.update_config(component, submission=self.submission, data={})

        self.assertEqual(component["values"], [])
        log = TimelineLogProxy.objects.for_object(self.submission.form).get()
        assert log.extra_data
        self.assertEqual(log.template, "logging/events/form_configuration_error.txt")
        self.assertEqual(
            log.extra_data["error"],
            _(
                "Cannot fetch from Referentielijsten API, because no `service` is configured."
            ),
        )

    def test_no_code_configured(self):
        component: RadioComponent = {
            "key": "radio",
            "type": "radio",
            "label": "Radio",
            "values": [],
            "dataType": "string",
            "openForms": {
                "code": "",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        with self.assertRaises(ServiceUnavailable):
            register.update_config(component, submission=self.submission, data={})

        self.assertEqual(component["values"], [])
        log = TimelineLogProxy.objects.for_object(self.submission.form).get()
        assert log.extra_data
        self.assertEqual(log.template, "logging/events/form_configuration_error.txt")
        self.assertEqual(
            log.extra_data["error"],
            _(
                "Cannot fetch from Referentielijsten API, because no `code` is configured."
            ),
        )

    def test_service_does_not_exist(self):
        component: RadioComponent = {
            "key": "radio",
            "type": "radio",
            "label": "Radio",
            "values": [],
            "dataType": "string",
            "openForms": {
                "code": "tabel1",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        self.service.delete()

        with self.assertRaises(ServiceUnavailable):
            register.update_config(component, submission=self.submission, data={})

        self.assertEqual(component["values"], [])
        log = TimelineLogProxy.objects.for_object(self.submission.form).get()
        assert log.extra_data
        self.assertEqual(log.template, "logging/events/form_configuration_error.txt")
        self.assertEqual(
            log.extra_data["error"],
            _(
                "Cannot fetch from Referentielijsten API, service with {service_slug} does not exist."
            ).format(service_slug=self.service.slug),
        )

    def test_items_not_found(self):
        component: RadioComponent = {
            "key": "radio",
            "type": "radio",
            "label": "Radio",
            "values": [],
            "dataType": "string",
            "openForms": {
                "code": "non-existent",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        with self.assertRaises(ServiceUnavailable):
            register.update_config(component, submission=self.submission, data={})

        self.assertEqual(component["values"], [])
        log = TimelineLogProxy.objects.for_object(self.submission.form).get()
        assert log.extra_data
        self.assertEqual(
            log.template, "logging/events/referentielijsten_failure_response.txt"
        )
        self.assertEqual(
            log.extra_data["error"],
            _("No results found from Referentielijsten API."),
        )

    @requests_mock.Mocker()
    def test_request_exception(self, m):
        component: RadioComponent = {
            "key": "radio",
            "type": "radio",
            "label": "Radio",
            "values": [],
            "dataType": "string",
            "openForms": {
                "code": "tabel1",
                "dataSrc": DataSrcOptions.referentielijsten,
                "service": self.service.slug,
                "translations": {},
            },
        }

        m.get(
            f"{self.service.api_root}items?tabel__code=tabel1",
            exc=RequestException("something went wrong"),
        )

        with self.assertRaises(ServiceUnavailable):
            register.update_config(component, submission=self.submission, data={})

        self.assertEqual(component["values"], [])
        log = TimelineLogProxy.objects.for_object(self.submission.form).get()
        assert log.extra_data
        self.assertEqual(
            log.template, "logging/events/referentielijsten_failure_response.txt"
        )
        self.assertEqual(
            log.extra_data["error"],
            _(
                "Exception occurred while fetching from Referentielijsten API: something went wrong."
            ),
        )


@tag("gh-4993")
class SubmissionStepDetailTest(SubmissionsMixin, APITestCase):
    def test_get_submissionstep_detail_raises_error_for_referentielijsten_if_service_is_incorrect(
        self,
    ):
        form = FormFactory.create(
            generate_minimal_setup=True,
            formstep__form_definition__configuration={
                "components": [
                    {
                        "key": "selectboxes",
                        "type": "selectboxes",
                        "label": "Selectboxes",
                        "values": [{"label": "", "value": ""}],
                        "dataType": "string",
                        "openForms": {
                            "code": "tabel1",
                            "dataSrc": DataSrcOptions.referentielijsten,
                            "service": "non-existent",
                            "translations": {},
                        },
                        "id": "ew0bwv7",
                    }
                ]
            },
        )
        submission = SubmissionFactory.create(form=form)
        endpoint = reverse(
            "api:submission-steps-detail",
            kwargs={
                "submission_uuid": submission.uuid,
                "step_uuid": form.formstep_set.get().uuid,
            },
        )
        self._add_submission_to_session(submission)

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        # the detail message should be passed for errors that occur when fetching referentielijsten
        self.assertEqual(
            response.json()["detail"],
            _("Could not retrieve options from Referentielijsten API."),
        )
