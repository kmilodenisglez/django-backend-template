"""Tests for enriched merchant currencies feature."""

from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from apps.subscriptions.services import NowPaymentsAPI


class EnrichedCurrenciesTests(TestCase):
    """Test enriched merchant currencies with full-currencies data."""

    def setUp(self):
        """Clear cache before each test."""
        cache.clear()
        self.api = NowPaymentsAPI("test_key")

    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()

    @patch.object(NowPaymentsAPI, "_call")
    def test_enriched_currencies_basic(self, mock_call):
        """Test basic enrichment flow with merchant coins and full currencies."""

        # Mock merchant/coins response
        def side_effect(method, endpoint, data=None):
            if endpoint == "merchant/coins":
                return {"selectedCurrencies": ["btc", "eth", "usdt"]}
            elif endpoint == "full-currencies":
                return {
                    "currencies": [
                        {
                            "code": "btc",
                            "name": "Bitcoin",
                            "network": "btc",
                            "logo_url": "/images/coins/btc.svg",
                            "ticker": "btc",
                        },
                        {
                            "code": "eth",
                            "name": "Ethereum",
                            "network": "eth",
                            "logo_url": "/images/coins/eth.svg",
                            "ticker": "eth",
                        },
                        {
                            "code": "usdt",
                            "name": "Tether USD",
                            "network": "trc20",
                            "logo_url": "/images/coins/usdt.svg",
                            "ticker": "usdt",
                        },
                    ]
                }
            return {}

        mock_call.side_effect = side_effect

        # Call enriched method
        result = self.api.get_merchant_coins_enriched()

        # Verify structure
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["code"], "btc")
        self.assertEqual(result[0]["name"], "Bitcoin")
        self.assertEqual(result[0]["network"], "btc")
        self.assertIn("nowpayments.io", result[0]["logo_url"])

        self.assertEqual(result[1]["code"], "eth")
        self.assertEqual(result[1]["name"], "Ethereum")

        self.assertEqual(result[2]["code"], "usdt")
        self.assertEqual(result[2]["name"], "Tether USD")
        self.assertEqual(result[2]["network"], "trc20")

    @patch.object(NowPaymentsAPI, "_call")
    def test_enriched_currencies_caching(self, mock_call):
        """Test that enriched currencies are cached."""

        def side_effect(method, endpoint, data=None):
            if endpoint == "merchant/coins":
                return {"selectedCurrencies": ["btc"]}
            elif endpoint == "full-currencies":
                return {
                    "currencies": [
                        {
                            "code": "btc",
                            "name": "Bitcoin",
                            "network": "btc",
                            "logo_url": "/images/coins/btc.svg",
                            "ticker": "btc",
                        }
                    ]
                }
            return {}

        mock_call.side_effect = side_effect

        # First call
        result1 = self.api.get_merchant_coins_enriched()
        self.assertEqual(len(result1), 1)

        # Second call should use cache
        result2 = self.api.get_merchant_coins_enriched()
        self.assertEqual(len(result2), 1)

        # Verify _call was only invoked twice (once for merchant, once for full)
        # not 4 times (which would be without caching)
        self.assertEqual(mock_call.call_count, 2)

    @patch.object(NowPaymentsAPI, "_call")
    def test_enriched_currencies_fallback_no_match(self, mock_call):
        """Test fallback when currency not found in full-currencies."""

        def side_effect(method, endpoint, data=None):
            if endpoint == "merchant/coins":
                return {"selectedCurrencies": ["unknown_coin"]}
            elif endpoint == "full-currencies":
                return {"currencies": []}
            return {}

        mock_call.side_effect = side_effect

        result = self.api.get_merchant_coins_enriched()

        # Should still return entry but with minimal data
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["code"], "unknown_coin")
        self.assertEqual(result[0]["name"], "unknown_coin")
        self.assertIsNone(result[0]["network"])
        self.assertIsNone(result[0]["logo_url"])

    @patch.object(NowPaymentsAPI, "_call")
    def test_enriched_currencies_logo_url_prepending(self, mock_call):
        """Test that relative logo URLs are converted to absolute."""

        def side_effect(method, endpoint, data=None):
            if endpoint == "merchant/coins":
                return ["btc"]
            elif endpoint == "full-currencies":
                return {
                    "currencies": [
                        {
                            "code": "btc",
                            "name": "Bitcoin",
                            "logo_url": "/images/coins/btc.svg",
                        }
                    ]
                }
            return {}

        mock_call.side_effect = side_effect

        result = self.api.get_merchant_coins_enriched()

        self.assertIn(
            "https://nowpayments.io/images/coins/btc.svg", result[0]["logo_url"]
        )

    @patch.object(NowPaymentsAPI, "_call")
    def test_enriched_currencies_merchant_list_response(self, mock_call):
        """Test handling merchant/coins as a list instead of dict."""

        def side_effect(method, endpoint, data=None):
            if endpoint == "merchant/coins":
                # Direct list response
                return ["btc", "eth"]
            elif endpoint == "full-currencies":
                return {
                    "currencies": [
                        {"code": "btc", "name": "Bitcoin", "logo_url": "/btc.svg"},
                        {"code": "eth", "name": "Ethereum", "logo_url": "/eth.svg"},
                    ]
                }
            return {}

        mock_call.side_effect = side_effect

        result = self.api.get_merchant_coins_enriched()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["code"], "btc")
        self.assertEqual(result[1]["code"], "eth")
