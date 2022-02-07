from os import getenv


BITMEX_WSS_URL = getenv('GW_BITMEX_WSS_URL', 'wss://ws.testnet.bitmex.com/realtime')
BITMEX_TESTNET_AUTH_KEYS = {
    'api_key': getenv('GW_BITMEX_API_KEY', 'PcXWyfcwRWE3ROLQ8Ltsc9Y_'),
    'api_secret': getenv('GW_BITMEX_API_SECRET', 'NKIMXt5653i_AgzaAzqJbaPko1z13sXAXz7SUcx0cYskYcZ6')
}
