from typing import Any

from django.core.cache import cache
from django.test import SimpleTestCase

from apps.subscriptions import views


class FakeAPI:
    """Mock NowPaymentsAPI for testing."""

    def __init__(self, coins: Any) -> None:
        self._coins = coins

    def get_merchant_coins(self) -> Any:
        """Simulate merchant/coins returning a dict or list."""
        return self._coins


class MerchantCurrenciesTests(SimpleTestCase):
    def setUp(self) -> None:
        # Ensure cache doesn't leak between tests
        cache.delete("nowpayments:merchant_currencies")

    def test_get_merchant_currencies_with_dict_response(self) -> None:
        """Test merchant currencies with NowPayments dict response format."""
        sample = {
            "selectedCurrencies": ["USDTTRC20", "USDCMATIC", "USDTBSC", "BTC", "ETH"]
        }
        api = FakeAPI(sample)  # type: ignore
        currencies = views._get_merchant_currencies(api)  # type: ignore

        # Should return all currencies
        self.assertEqual(len(currencies), 5)
        self.assertIn("USDTTRC20", currencies)
        self.assertIn("BTC", currencies)
        self.assertIn("ETH", currencies)

    def test_get_merchant_currencies_with_list_response(self) -> None:
        """Test merchant currencies with plain list response."""
        sample = ["BTC", "ETH", "USDTBSC"]
        api = FakeAPI(sample)  # type: ignore
        currencies = views._get_merchant_currencies(api)  # type: ignore

        # Should return all currencies
        self.assertEqual(len(currencies), 3)
        self.assertIn("BTC", currencies)
        self.assertIn("USDTBSC", currencies)

    def test_get_merchant_currencies_normalizes_duplicates(self) -> None:
        """Test that normalized duplicates are excluded."""
        sample = {"selectedCurrencies": ["btc", "BTC", "Btc", "ETH"]}
        api = FakeAPI(sample)  # type: ignore
        currencies = views._get_merchant_currencies(api)  # type: ignore

        # Should have 2 unique normalized codes (btc and eth)
        self.assertEqual(len(currencies), 2)

    def test_get_merchant_currencies_empty(self) -> None:
        """Test handling of empty currency list."""
        sample = []
        api = FakeAPI(sample)  # type: ignore
        currencies = views._get_merchant_currencies(api)  # type: ignore
        self.assertEqual(currencies, [])

    def test_get_merchant_currencies_caching(self) -> None:
        """Test that results are cached."""
        sample = {"selectedCurrencies": ["BTC", "ETH"]}
        api = FakeAPI(sample)  # type: ignore

        # First call
        currencies1 = views._get_merchant_currencies(api)  # type: ignore
        self.assertEqual(len(currencies1), 2)

        # Change the data in FakeAPI
        api._coins = {"selectedCurrencies": ["BTC"]}

        # Second call should return cached result
        currencies2 = views._get_merchant_currencies(api)  # type: ignore
        self.assertEqual(len(currencies2), 2)  # Still 2, from cache
