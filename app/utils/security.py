import hmac
import hashlib
import os
from flask import abort

GITHUB_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

def is_valid_signature(request):
    header_signature = request.headers.get('X-Hub-Signature-256')
    if header_signature is None:
        return False

    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha256':
        return False

    mac = hmac.new(GITHUB_SECRET.encode(), msg=request.data, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)
