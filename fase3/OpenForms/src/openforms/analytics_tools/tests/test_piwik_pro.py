from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse

from cookie_consent.models import Cookie
from rest_framework import status
from rest_framework.test import APITestCase

from openforms.config.models import CSPSetting
from openforms.forms.tests.factories import FormFactory
from openforms.tests.test_csp import CSPMixin

from ..constants import AnalyticsTools
from .mixin import AnalyticsMixin


@override_settings(SOLO_CACHE=None, BASE_URL="https://example.com:8443/foo")
class PiwikProTests(AnalyticsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.piwik_pro_url = "https://example.com"
        cls.json_cookies = [
            {"name": "_pk_id.771cbcaa-7315-4663-ba47-88f9a8cc158c.8809", "path": "/"},
            {"name": "_pk_ses.771cbcaa-7315-4663-ba47-88f9a8cc158c.8809", "path": "/"},
        ]

        cls.json_csp = [
            {"directive": "default-src", "value": cls.piwik_pro_url},
        ]

    def test_piwik_pro_properly_enabled(self):
        self.config.piwik_pro_url = self.piwik_pro_url
        self.config.piwik_pro_site_id = "771cbcaa-7315-4663-ba47-88f9a8cc158c"

        self.config.enable_piwik_pro_site_analytics = True
        self.config.clean()
        self.config.save()

        for cookie in self.json_cookies:
            with self.subTest("Test creation of cookies"):
                try:
                    Cookie.objects.get(name=cookie["name"])
                except Cookie.DoesNotExist as e:
                    self.fail(f"Unexpected exception : {e}")

        for csp in self.json_csp:
            with self.subTest("Test creation of CSP"):
                try:
                    CSPSetting.objects.get(
                        value=csp["value"],
                        directive=csp["directive"],
                        identifier=AnalyticsTools.piwik_pro,
                    )
                except CSPSetting.DoesNotExist as e:
                    self.fail(f"Unexpected exception : {e}")

    def test_piwik_pro_properly_disabled(self):
        self.config.piwik_pro_url = self.piwik_pro_url
        self.config.piwik_pro_site_id = "771cbcaa-7315-4663-ba47-88f9a8cc158c"

        # creation of cookies
        self.config.enable_piwik_pro_site_analytics = True
        self.config.clean()
        self.config.save()

        # Deletion of cookies
        self.config.enable_piwik_pro_site_analytics = False
        self.config.clean()
        self.config.save()

        for cookie in self.json_cookies:
            with self.subTest("Test deletion of cookies"):
                self.assertFalse(Cookie.objects.filter(name=cookie["name"]).exists())

        for csp in self.json_csp:
            with self.subTest("Test deletion of CSP"):
                self.assertFalse(
                    CSPSetting.objects.filter(
                        value=csp["value"],
                        directive=csp["directive"],
                        identifier=AnalyticsTools.piwik_pro,
                    ).exists()
                )

    def test_piwik_pro_enabled_but_related_fields_are_not(self):
        self.config.enable_piwik_pro_site_analytics = True

        with self.assertRaises(ValidationError):
            self.config.clean()


@override_settings(CSP_DEFAULT_SRC=["'self'"], CSP_REPORT_ONLY=False)
class CanLoadFormWithAnalyticsCSPTests(CSPMixin, APITestCase):
    def test_loading_form_still_has_self_in_default_src(self):
        csp_setting = CSPSetting(value="https://piwikpro.com", directive="default-src")
        csp_setting.save()

        form = FormFactory.create()

        response = self.client.get(
            reverse("core:form-detail", kwargs={"slug": form.slug})
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn(
            "default-src 'self' https://piwikpro.com",
            response.headers["Content-Security-Policy"],
        )
