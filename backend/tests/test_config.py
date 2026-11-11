"""Unit test for application configuration and security baseline."""

import unittest
from app.core.config import Settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)


class TestSecurityBaseline(unittest.TestCase):
    """Verify security functions meet cryptographic baseline."""

    def test_settings_initialization(self):
        settings = Settings()
        self.assertEqual(settings.APP_NAME, "AapadaOps")
        self.assertEqual(settings.DEFAULT_SRID, 4326)
        self.assertIn("min_lat", settings.ODISHA_BOUNDS)

    def test_password_hashing_and_verification(self):
        password = "SpecialReliefCommissioner#2026"
        hashed = get_password_hash(password)
        self.assertNotEqual(password, hashed)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPassword123", hashed))

    def test_jwt_generation_and_decoding(self):
        subject = "officer_puri_01"
        role = "DISTRICT_COLLECTOR"
        district = "Puri"
        token = create_access_token(subject=subject, role=role, district=district)
        self.assertIsInstance(token, str)

        payload = decode_access_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload.get("sub"), subject)
        self.assertEqual(payload.get("role"), role)
        self.assertEqual(payload.get("district"), district)


if __name__ == "__main__":
    unittest.main()

