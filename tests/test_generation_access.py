import unittest
from unittest.mock import Mock

from api.generation_access import GenerationAccessError, admit_generation

FEATURE = '11111111-1111-4111-8111-111111111111'
CUSTOMER = '22222222-2222-4222-8222-222222222222'
ENV = {'LONGPLAY_GENERATION_FEATURE_ID': FEATURE, 'LONGPLAY_BASE_URL': 'https://billing.invalid',
       'LONGPLAY_APP_ID': 'app', 'LONGPLAY_ENVIRONMENT': 'sandbox', 'LONGPLAY_SECRET_KEY': 'gg_sk_' + 'x' * 43}


class GenerationAccessTests(unittest.TestCase):
    def setUp(self):
        self.user = Mock(return_value='verified-user')
        self.allowed = True
        self.kind = 'access'
        self.calls = []

    def post(self, path, body):
        self.calls.append((path, body))
        data = {'requestId': CUSTOMER, 'scope': {'projectId': 'app', 'environment': 'sandbox'}}
        if path == 'customers':
            data['customer'] = {'id': CUSTOMER}
        else:
            data['check'] = {'internal_feature_id': FEATURE, 'kind': self.kind, 'allowed': self.allowed}
        return data

    def test_default_local_mode_does_not_require_auth_or_billing(self):
        admit_generation(None, self.user, {}, self.post)
        self.user.assert_not_called()
        self.assertEqual(self.calls, [])

    def test_missing_authentication_precedes_billing(self):
        with self.assertRaises(GenerationAccessError) as error:
            admit_generation(None, self.user, ENV, self.post)
        self.assertEqual(error.exception.status, 401)
        self.assertEqual(self.calls, [])

    def test_trusted_database_identity_is_the_only_customer_selector(self):
        admit_generation('Bearer account-session', self.user, ENV, self.post)
        self.user.assert_called_once_with('account-session')
        self.assertEqual(self.calls, [('customers', {'externalUserId': 'jan:user:verified-user'}),
                                     ('entitlements/check', {'customerId': CUSTOMER, 'requirement': {
                                         'internal_feature_id': FEATURE, 'quantity': '1', 'properties': {}}})])

    def test_revocation_is_observed_on_the_next_generation(self):
        admit_generation('Bearer session', self.user, ENV, self.post)
        self.allowed = False
        with self.assertRaises(GenerationAccessError) as error:
            admit_generation('Bearer session', self.user, ENV, self.post)
        self.assertEqual(error.exception.status, 402)

    def test_credit_checks_and_wrong_scope_fail_closed(self):
        self.kind = 'credit'
        with self.assertRaises(GenerationAccessError):
            admit_generation('Bearer session', self.user, ENV, self.post)
        with self.assertRaises(GenerationAccessError):
            admit_generation('Bearer session', self.user, ENV, lambda *_: {'scope': {'projectId': 'foreign'}})

    def test_configuration_and_service_failures_are_sanitized(self):
        with self.assertRaises(GenerationAccessError):
            admit_generation('Bearer session', self.user, {'LONGPLAY_GENERATION_FEATURE_ID': FEATURE}, self.post)
        self.assertEqual(self.calls, [])
        with self.assertRaises(GenerationAccessError) as error:
            admit_generation('Bearer session', self.user, ENV, Mock(side_effect=RuntimeError('PRIVATE')))
        self.assertEqual(str(error.exception), 'billing_unavailable')

    def test_failed_account_verification_never_reaches_billing(self):
        with self.assertRaises(PermissionError):
            admit_generation('Bearer forged', Mock(side_effect=PermissionError()), ENV, self.post)
        self.assertEqual(self.calls, [])


if __name__ == '__main__':
    unittest.main()
