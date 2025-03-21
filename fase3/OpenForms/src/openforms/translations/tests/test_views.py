import json

from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase


class FormioTranslationsEndpointTests(APITestCase):
    # TODO: deprecated, remove when the deprecated view is removed
    def test_returns_translations(self):
        response = self.client.get(reverse("api:translations:formio-translations"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("nl", response.json())

    def test_language_code_param(self):
        endpoint = reverse("api:i18n:formio-translations", kwargs={"language": "nl"})

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/json")
        content = b"".join(x for x in response.streaming_content)
        translations = json.loads(content)
        self.assertNotIn("nl", translations)
        self.assertGreater(len(translations), 0, "No Dutch translations returned")

    def test_unsupported_language_code(self):
        endpoint = reverse("api:i18n:formio-translations", kwargs={"language": "sw"})

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_all_supported_languages_present(self):
        for code, language in settings.LANGUAGES:
            with self.subTest(language=language, code=code):
                endpoint = reverse(
                    "api:i18n:formio-translations", kwargs={"language": code}
                )

                response = self.client.get(endpoint)

                self.assertEqual(response.status_code, status.HTTP_200_OK)
