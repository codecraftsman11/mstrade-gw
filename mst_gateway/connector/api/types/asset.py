def to_system_asset(asset: str):
    system_asset = asset.lower()
    if system_asset == 'xbt':
        system_asset = 'btc'
    elif system_asset == 'usdt':
        system_asset = 'usd'
    return system_asset
