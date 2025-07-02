import ssl
import requests
from urllib3.poolmanager import PoolManager
from requests.adapters import HTTPAdapter

class TLSAdapter(HTTPAdapter):
    """
    A Requests TransportAdapter that uses a custom SSLContext
    (so you can specify ciphers, minimum TLS version, etc).
    """
    def __init__(self, ssl_context: ssl.SSLContext, **kwargs):
        self._ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        # Called when building the urllib3 PoolManager
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self._ssl_context,
            **pool_kwargs
        )

# 1) Create an SSLContext that only allows AES256-GCM-SHA384
ctx = ssl.create_default_context()          # picks up your system CAs, etc
ctx.set_ciphers("AES256-GCM-SHA384")        # whitelist exactly this suite
# (you can also call ctx.options |= ssl.OP_NO_TLSv1 to disable TLS1.0, etc)

# 2) Mount it on your session
session = requests.Session()
session.mount("https://", TLSAdapter(ctx))

# 3) Use `session` everywhere instead of `requests`
resp = session.get("https://masterdeploy.int.ca.cib/…")

