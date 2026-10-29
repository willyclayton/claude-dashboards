import os
import sys
import time

import jwt

secret = os.environ["CUBEJS_API_SECRET"]
payload = {"exp": int(time.time()) + 3600}
if len(sys.argv) > 1 and sys.argv[1]:
    payload["country"] = sys.argv[1]

print(jwt.encode(payload, secret, algorithm="HS256"))
