from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from openforms.accounts.tests.factories import SuperUserFactory
from openforms.forms.tests.factories import FormFactory


class FormRegistrationBackendOptionsTests(APITestCase):
    """
    Test configuring a form with the appropriate Camunda options.

    This mostly tests the full ``CamundaOptionsSerializer``.

    TODO: add a test for a mapped variable that does not exist on the form.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = SuperUserFactory.create()
        cls.form = FormFactory.create(
            generate_minimal_setup=True,
            registration_backend="camunda",
            formstep__form_definition__configuration={
                "components": [
                    {
                        "key": "test1",
                        "type": "textfield",
                    },
                    {
                        "key": "test2",
                        "type": "textfield",
                    },
                    {
                        "key": "test3",
                        "type": "textfield",
                    },
                ],
            },
        )
        cls.endpoint = reverse(
            "api:form-detail", kwargs={"uuid_or_slug": cls.form.uuid}
        )

    def setUp(self):
        super().setUp()

        self.client.force_authenticate(user=self.user)

    def test_happy_flow(self):
        """
        Assert that options are saved correctly.
        """
        self.maxDiff = None
        detail_response = self.client.get(self.endpoint).json()

        data = {
            **detail_response,
            "registrationBackends": [
                {
                    "name": "Foo",
                    "key": "camunda-fu",
                    "backend": "camunda",
                    "options": {
                        "processDefinition": "invoice",
                        "processDefinitionVersion": None,
                        "processVariables": [
                            {
                                "enabled": True,
                                "componentKey": "test1",
                            },
                            {
                                "enabled": False,
                                "componentKey": "test2",
                                "alias": "test2Alias",
                            },
                        ],
                        "complexProcessVariables": [
                            {
                                "enabled": True,
                                "alias": "complex1",
                                "type": "object",
                                "definition": {
                                    "fooBar": {  # deliberate camelCase key - should not be converted to underscore
                                        "source": "manual",
                                        "type": "string",
                                        "definition": "bar",
                                    }
                                },
                            },
                            {
                                "enabled": False,
                                "alias": "complex2",
                                "type": "array",
                                "definition": [
                                    {
                                        "source": "component",
                                        "definition": {"var": "test1"},
                                    },
                                ],
                            },
                        ],
                    },
                }
            ],
        }

        response = self.client.put(self.endpoint, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.form.refresh_from_db()
        expected = {
            "process_definition": "invoice",
            "process_definition_version": None,
            "process_variables": [
                {
                    "enabled": True,
                    "component_key": "test1",
                    "alias": "",
                },
                {
                    "enabled": False,
                    "component_key": "test2",
                    "alias": "test2Alias",
                },
            ],
            "complex_process_variables": [
                {
                    "enabled": True,
                    "alias": "complex1",
                    "type": "object",
                    "definition": {
                        "fooBar": {
                            "source": "manual",
                            "type": "string",
                            "definition": "bar",
                        }
                    },
                },
                {
                    "enabled": False,
                    "alias": "complex2",
                    "type": "array",
                    "definition": [
                        {
                            "source": "component",
                            "definition": {"var": "test1"},
                        }
                    ],
                },
            ],
        }
        self.assertEqual(self.form.registration_backends.first().options, expected)

    def test_read_complex_variables(self):
        """
        Test that complex variables are not converted into camelCase.
        """
        self.maxDiff = None
        form = FormFactory.create(
            generate_minimal_setup=True,
            registration_backend="camunda",
            formstep__form_definition__configuration={
                "components": [
                    {
                        "key": "test1",
                        "type": "textfield",
                    },
                ]
            },
            registration_backend_options={
                "process_definition": "invoice",
                "process_definition_version": None,
                "process_variables": [],
                "complex_process_variables": [
                    {
                        "enabled": True,
                        "alias": "complex1",
                        "type": "object",
                        "definition": {
                            "snake_case": {
                                "source": "manual",
                                "type": "object",
                                "definition": {
                                    "nested_var1": {
                                        "source": "manual",
                                        "type": "null",
                                        "definition": None,
                                    },
                                },
                            },
                            "camelCase": {
                                "source": "manual",
                                "type": "object",
                                "definition": {
                                    "nestedVar2": {
                                        "source": "manual",
                                        "type": "null",
                                        "definition": None,
                                    },
                                },
                            },
                        },
                    }
                ],
            },
        )
        endpoint = reverse("api:form-detail", kwargs={"uuid_or_slug": form.uuid})

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        complex_var = response.json()["registrationBackends"][0]["options"][
            "complexProcessVariables"
        ][0]
        expected = {
            "snake_case": {
                "source": "manual",
                "type": "object",
                "definition": {
                    "nested_var1": {
                        "source": "manual",
                        "type": "null",
                        "definition": None,
                    },
                },
            },
            "camelCase": {
                "source": "manual",
                "type": "object",
                "definition": {
                    "nestedVar2": {
                        "source": "manual",
                        "type": "null",
                        "definition": None,
                    },
                },
            },
        }
        self.assertEqual(complex_var["definition"], expected)

    def test_process_vars_incomplete_data(self):
        invalid_vars = [
            {},
            None,
            {"enabled": True, "componentKey": ""},
            # {"enabled": True, "componentKey": "non-existent"},
        ]
        expected_errors = [
            {
                "registrationBackends.0.options.processVariables.0.enabled": "required",
                "registrationBackends.0.options.processVariables.0.componentKey": "required",
            },
            {
                "registrationBackends.0.options.processVariables": "null",
            },
            {
                "registrationBackends.0.options.processVariables.0.componentKey": "blank",
            },
        ]

        for invalid_var, expected_error_codes in zip(invalid_vars, expected_errors):
            with self.subTest(invalid_var=invalid_var):
                data = {
                    "registrationBackends": [
                        {
                            "backend": "camunda",
                            "key": "test1",
                            "options": {
                                "processDefinition": "invoice",
                                "processDefinitionVersion": None,
                                "processVariables": [invalid_var],
                                "complexProcessVariables": [],
                            },
                        }
                    ]
                }

                response = self.client.patch(self.endpoint, data)

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                error_codes = {
                    param["name"]: param["code"]
                    for param in response.json()["invalidParams"]
                }
                self.assertEqual(error_codes, expected_error_codes)

    def test_complex_process_vars_incomplete_data(self):
        invalid_vars = [
            {},
            None,
            {"enabled": True, "alias": ""},
            {"enabled": True, "alias": "test", "type": ""},
            {"enabled": True, "alias": "test", "type": "object", "definition": None},
            {"enabled": True, "alias": "test", "type": "object", "definition": []},
        ]
        expected_errors = [
            {
                "registrationBackends.0.options.complexProcessVariables.0.enabled": "required",
                "registrationBackends.0.options.complexProcessVariables.0.alias": "required",
                "registrationBackends.0.options.complexProcessVariables.0.type": "required",
            },
            {
                "registrationBackends.0.options.complexProcessVariables": "null",
            },
            {
                "registrationBackends.0.options.complexProcessVariables.0.alias": "blank",
                "registrationBackends.0.options.complexProcessVariables.0.type": "required",
            },
            {
                "registrationBackends.0.options.complexProcessVariables.0.type": "invalid_choice",
            },
            {
                "registrationBackends.0.options.complexProcessVariables.0.definition": "null",
            },
            {
                "registrationBackends.0.options.complexProcessVariables.0.definition": "not_a_dict",
            },
        ]

        for invalid_var, expected_error_codes in zip(invalid_vars, expected_errors):
            with self.subTest(invalid_var=invalid_var):
                data = {
                    "registrationBackends": [
                        {
                            "backend": "camunda",
                            "key": "test1",
                            "options": {
                                "processDefinition": "invoice",
                                "processDefinitionVersion": None,
                                "processVariables": [],
                                "complexProcessVariables": [invalid_var],
                            },
                        }
                    ]
                }

                response = self.client.patch(self.endpoint, data)

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                error_codes = {
                    param["name"]: param["code"]
                    for param in response.json()["invalidParams"]
                }
                self.assertEqual(error_codes, expected_error_codes)

    def test_simple_and_complex_overlapping_variable_names(self):
        detail_response = self.client.get(self.endpoint).json()
        data = {
            **detail_response,
            "registrationBackends": [
                {
                    "name": "Camunda",
                    "key": "camunda",
                    "backend": "camunda",
                    "options": {
                        "processDefinition": "invoice",
                        "processDefinitionVersion": None,
                        "processVariables": [
                            {
                                "enabled": True,
                                "componentKey": "test1",
                            },
                            {
                                "enabled": True,
                                "componentKey": "test2",
                                "alias": "test2Alias",
                            },
                        ],
                        "complexProcessVariables": [
                            {
                                "enabled": True,
                                "alias": "test1",
                                "type": "object",
                                "definition": {
                                    "fooBar": {
                                        "source": "manual",
                                        "type": "string",
                                        "definition": "bar",
                                    }
                                },
                            },
                            {
                                "enabled": False,
                                "alias": "test2Alias",
                                "type": "array",
                                "definition": [
                                    {
                                        "source": "component",
                                        "definition": {"var": "test1"},
                                    },
                                ],
                            },
                        ],
                    },
                }
            ],
        }

        response = self.client.put(self.endpoint, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = response.json()["invalidParams"][0]
        self.assertEqual(error["code"], "duplicate-variables")
