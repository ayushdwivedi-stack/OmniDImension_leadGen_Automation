import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Ensure current dir is in path
sys.path.insert(0, str(Path(__file__).parent))

import config
config.AGENT_ID = "42"
config.OMNIDIM_API_KEY = "test_key_12345"

from omnidim_client import OmniDimClient


class TestOmniDimClient(unittest.TestCase):
    def setUp(self):
        self.client = OmniDimClient("test_key_12345", agent_id=42)

    def test_phone_number_normalization(self):
        self.assertEqual(
            OmniDimClient.normalize_phone_number("+15551234567"),
            "+15551234567"
        )
        self.assertEqual(
            OmniDimClient.normalize_phone_number("15551234567"),
            "+15551234567"
        )
        self.assertEqual(
            OmniDimClient.normalize_phone_number("+1 (555) 123-4567"),
            "+15551234567"
        )
        self.assertIsNone(OmniDimClient.normalize_phone_number("invalid_phone"))
        self.assertIsNone(OmniDimClient.normalize_phone_number("123"))  # too short
        self.assertIsNone(OmniDimClient.normalize_phone_number(""))

    def test_missing_agent_id_raises_value_error(self):
        with self.assertRaises(ValueError):
            OmniDimClient("test_key", agent_id="")

    @patch("requests.post")
    def test_dispatch_call_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"call_id": "call_abc_123"}
        mock_post.return_value = mock_response

        lead_data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "lead_id": "lead_987"
        }

        call_id = self.client.dispatch_call("+15551234567", lead_data)
        self.assertEqual(call_id, "call_abc_123")

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://backend.omnidim.io/api/v1/calls/dispatch")
        self.assertEqual(kwargs["json"]["to_number"], "+15551234567")
        self.assertEqual(kwargs["json"]["agent_id"], 42)
        self.assertEqual(kwargs["json"]["call_context"]["customer_name"], "Jane Doe")
        self.assertEqual(kwargs["timeout"], 30.0)

    @patch("requests.post")
    def test_dispatch_call_invalid_phone_skips_network(self, mock_post):
        call_id = self.client.dispatch_call("not-a-number", {"name": "Test"})
        self.assertIsNone(call_id)
        mock_post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
