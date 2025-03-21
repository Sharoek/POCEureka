from unittest.mock import patch

from django.test import TestCase

from ..tasks import maybe_hash_identifying_attributes
from .factories import SubmissionFactory


class HashIdentifyingAttributesTaskTests(TestCase):
    @patch("openforms.authentication.models.AuthInfo.hash_identifying_attributes")
    def test_registration_not_succesful(self, mock_hash):
        submissions = [
            SubmissionFactory.create(
                completed=True,
                auth_info__attribute_hashed=False,
                registration_failed=True,
            ),
            SubmissionFactory.create(
                completed=True,
                auth_info__attribute_hashed=False,
                registration_pending=True,
            ),
            SubmissionFactory.create(
                completed=True,
                auth_info__attribute_hashed=False,
                registration_in_progress=True,
            ),
        ]

        for submission in submissions:
            with self.subTest(registration_status=submission.registration_status):
                maybe_hash_identifying_attributes(submission.id)

                submission.refresh_from_db()
                self.assertFalse(submission.auth_info.attribute_hashed)
                mock_hash.assert_not_called()

    def test_already_hashed(self):
        submission = SubmissionFactory.create(
            completed=True,
            auth_info__attribute_hashed=True,
            registration_success=True,
        )

        maybe_hash_identifying_attributes(submission.id)

        submission.refresh_from_db()
        self.assertTrue(submission.auth_info.attribute_hashed)
