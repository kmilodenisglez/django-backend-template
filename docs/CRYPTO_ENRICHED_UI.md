# Enriched Cryptocurrency Selection UI

## Overview
The crypto payment selection now displays rich information about each currency using data from both NowPayments API endpoints in an optimized way.

## Implementation Details

### API Strategy
1. **Merchant Coins** (`/v1/merchant/coins`) - Fast, fetches your enabled currencies
2. **Full Currencies** (`/v1/full-currencies`) - Expensive, called once per 24h and cached

### Caching Architecture
```
┌─────────────────────────────────────────────────────┐
│  User requests crypto payment page                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  Check enriched merchant cache (60s TTL)            │
│  Cache key: nowpayments:merchant_currencies_enriched│
└──────────────────┬──────────────────────────────────┘
                   │
                   ├─── HIT ──────► Return cached data
                   │
                   └─── MISS
                        │
                        ▼
            ┌──────────────────────────┐
            │ Fetch merchant/coins      │
            │ (cheap, fast)             │
            └──────────┬────────────────┘
                       │
                       ▼
            ┌──────────────────────────┐
            │ Check full currencies    │
            │ cache (24h TTL)          │
            └──────────┬────────────────┘
                       │
                       ├─── HIT ──────┐
                       │               │
                       └─── MISS       │
                            │          │
                            ▼          │
                    ┌──────────────┐  │
                    │ Call full-   │  │
                    │ currencies   │  │
                    │ (expensive)  │  │
                    └──────┬───────┘  │
                           │          │
                           └──────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ Match & enrich data  │
                    │ - code               │
                    │ - name               │
                    │ - network            │
                    │ - logo_url           │
                    └──────┬───────────────┘
                           │
                           ▼
                    ┌──────────────────────┐
                    │ Cache enriched data  │
                    │ (60s TTL)            │
                    └──────────────────────┘
```

### Performance Benefits
- **First load**: 2 API calls (merchant + full), then cached for 24h
- **Subsequent loads**: 0 API calls (enriched cache, 60s TTL)
- **After 60s**: 1 API call (merchant only, full still cached)
- **After 24h**: 2 API calls (refresh both)

### UI Features

#### Currency Dropdown
Each option shows:
- **Currency logo** (icon)
- **Full name** (e.g., "Bitcoin")
- **Currency code** (e.g., "BTC")
- **Network** (e.g., "TRC20" for USDT)

Example display:
```
🪙 Bitcoin (BTC) - BTC
💎 Ethereum (ETH) - ETH
💵 Tether USD (USDT) - TRC20
🟣 Polygon (MATIC) - POLYGON
```

#### Live Preview Card
When user selects a currency:
```
┌─────────────────────────────────┐
│ 🪙 Bitcoin                      │
│    BTC • BTC                     │
└─────────────────────────────────┘
```

#### Single Currency Auto-selection
When only one currency available:
```
┌─────────────────────────────────────┐
│ 🪙 Tether USD                       │
│    USDT • TRC20 • Auto-selected     │
└─────────────────────────────────────┘
```

## Code Structure

### Backend (`apps/subscriptions/services.py`)
```python
class NowPaymentsAPI:
    def get_merchant_coins_enriched(
        self,
        merchant_ttl: int = 60,
        full_ttl: int = 60 * 60 * 24,
    ) -> List[Dict[str, Any]]:
        """Returns enriched merchant currencies with name, network, logo."""
        # Returns: [
        #   {
        #     "code": "btc",
        #     "name": "Bitcoin",
        #     "network": "btc",
        #     "logo_url": "https://nowpayments.io/images/coins/btc.svg",
        #     "raw": {...full currency data...}
        #   }
        # ]
```

### View (`apps/subscriptions/views.py`)
```python
@login_required
def crypto_payment_selection(request, plan_id):
    api = provider.get_api()
    currencies = api.get_merchant_coins_enriched()
    # currencies now has rich data for template
```

### Template (`templates/subscriptions/crypto_selection.html`)
```html
<select name="currency" id="currency">
    {% for currency in currencies %}
        <option value="{{ currency.code }}"
                data-name="{{ currency.name }}"
                data-network="{{ currency.network }}"
                data-logo="{{ currency.logo_url }}">
            {{ currency.name }} ({{ currency.code|upper }})
            {% if currency.network %} - {{ currency.network|upper }}{% endif %}
        </option>
    {% endfor %}
</select>

<!-- Preview updates via JavaScript -->
<div id="currency-preview"></div>
```

## Testing

### Unit Tests
Located in: `apps/subscriptions/tests/test_enriched_currencies.py`

Coverage:
- ✅ Basic enrichment flow
- ✅ Caching behavior
- ✅ Fallback for unmatched currencies
- ✅ Logo URL prepending
- ✅ Different merchant response formats

Run tests:
```bash
PYTHONPATH=/home/kmilo/Downloads/developer/isowo DJANGO_SETTINGS_MODULE=config.settings poetry run pytest apps/subscriptions/tests/test_enriched_currencies.py -v
```

## Backward Compatibility

The implementation maintains full backward compatibility:
- If `full-currencies` call fails, falls back to plain currency codes
- If currency not found in full list, shows code as name
- Existing estimate/invoice endpoints unchanged
- Works with both dict and list merchant response formats

## Configuration

### Cache TTLs (customizable)
```python
# Short cache for merchant list (user sees fresh data)
merchant_ttl = 60  # 1 minute

# Long cache for full currencies (expensive call)
full_ttl = 60 * 60 * 24  # 24 hours
```

### Cache Keys
```python
cache_key_merchant = "nowpayments:merchant_currencies_enriched"
cache_key_full = "nowpayments:full_currencies"
```

## Future Enhancements

### Potential Improvements
1. **Custom Dropdown Library**: Replace native `<select>` with Select2 or Choices.js for better logo rendering
2. **Currency Icons**: Add fallback icons for currencies without logos
3. **Network Badges**: Color-coded badges for different networks (ERC20=blue, TRC20=red, etc.)
4. **Popular/Trending**: Show popular currencies first based on `is_popular` flag
5. **Search/Filter**: Add search functionality for large currency lists
6. **Mobile Optimization**: Touch-friendly selection with larger tap targets

### Example Enhanced UI (Future)
```
┌────────────────────────────────────────┐
│  🔍 Search currencies...               │
└────────────────────────────────────────┘

Popular
┌────────────────────────────────────────┐
│ 🪙 Bitcoin (BTC)                  ⭐   │
│    Network: BTC • Fee: Low             │
├────────────────────────────────────────┤
│ 💎 Ethereum (ETH)                 ⭐   │
│    Network: ETH • Fee: Medium          │
└────────────────────────────────────────┘

Stablecoins
┌────────────────────────────────────────┐
│ 💵 Tether USD (USDT)              🔵   │
│    Networks: TRC20, ERC20, BEP20       │
└────────────────────────────────────────┘
```

## Troubleshooting

### Cache not working?
```python
# Clear cache manually
from django.core.cache import cache
cache.delete('nowpayments:merchant_currencies_enriched')
cache.delete('nowpayments:full_currencies')
```

### Logo not showing?
- Check if `logo_url` starts with `/` (relative path)
- Implementation auto-prepends `https://nowpayments.io`
- Verify NowPayments API returns valid logo paths

### Currency not enriched?
- Check matching logic (code, ticker, name, cg_id)
- Currency codes are normalized (lowercase, alphanumeric only)
- Falls back gracefully to plain code if no match

## API Response Examples

### Merchant Coins Response
```json
{
  "selectedCurrencies": ["btc", "eth", "usdt", "usdttrc20"]
}
```

### Full Currencies Response (single entry)
```json
{
  "currencies": [
    {
      "id": 1,
      "code": "btc",
      "name": "Bitcoin",
      "enable": true,
      "wallet_regex": "^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$",
      "logo_url": "/images/coins/btc.svg",
      "network": "btc",
      "ticker": "btc",
      "is_popular": true,
      "available_for_payment": true
    }
  ]
}
```

### Enriched Output
```python
[
  {
    "code": "btc",
    "name": "Bitcoin",
    "network": "btc",
    "logo_url": "https://nowpayments.io/images/coins/btc.svg",
    "raw": {...}  # Full API data for advanced use
  }
]
```

## Summary

✅ **Optimized**: Minimizes expensive API calls with smart caching
✅ **Fast**: 60s cache for enriched data, 24h cache for full currencies
✅ **Rich UI**: Shows name, network, and logo for better UX
✅ **Tested**: Comprehensive unit test coverage
✅ **Compatible**: Works with existing code, graceful fallbacks
✅ **Scalable**: Handles both small and large currency lists efficiently
