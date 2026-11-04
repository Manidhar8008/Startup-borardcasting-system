"""Optional account-level content-generation admission, not tenant isolation or usage accounting."""

import json
import os
import re
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

UUID = re.compile(r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$", re.I)


class GenerationAccessError(RuntimeError):
    def __init__(self, status, code):
        super().__init__(code)
        self.status = status
        self.code = code


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None


def admit_generation(authorization, require_user, env=None, post=None):
    """require_user verifies the existing JWT/account and returns its database ID.

    Local mode does not initialize auth or billing. A request never supplies its
    billing Customer ID; topic, drafts, provider keys and brand data stay local.
    """
    env = os.environ if env is None else env
    feature = env.get("LONGPLAY_GENERATION_FEATURE_ID")
    if not feature:
        return
    match = re.fullmatch(r"Bearer ([^\s]+)", authorization or "", re.I)
    if not match:
        raise GenerationAccessError(401, "authentication_required")
    user_id = require_user(match.group(1))
    if not user_id:
        raise GenerationAccessError(401, "authentication_required")
    try:
        base = urlsplit(env.get("LONGPLAY_BASE_URL", ""))
        key = env.get("LONGPLAY_SECRET_KEY", "")
        app_id = env.get("LONGPLAY_APP_ID", "")
        environment = env.get("LONGPLAY_ENVIRONMENT", "")
        if (base.scheme != "https" or not base.netloc or base.username or base.password
                or base.path not in ("", "/") or base.query or base.fragment
                or not app_id or environment not in ("sandbox", "live")
                or not re.fullmatch(r"gg_sk_[A-Za-z0-9_-]{32,128}", key)
                or not UUID.fullmatch(feature)):
            raise ValueError("Configuration")

        def send(path, body):
            request = Request(env["LONGPLAY_BASE_URL"].rstrip("/") + "/api/v1/" + path,
                              data=json.dumps(body).encode(), method="POST", headers={
                                  "Content-Type": "application/json", "Authorization": "Bearer " + key,
                                  "X-Indiana-Protocol": "0.10", "X-Indiana-Project": app_id,
                                  "X-Indiana-Environment": environment})
            with build_opener(_NoRedirect()).open(request, timeout=3) as response:
                if response.headers.get("X-Indiana-Protocol") != "0.10":
                    raise ValueError("Protocol mismatch")
                raw = response.read(262145)
                if len(raw) > 262144:
                    raise ValueError("Response too large")
                return json.loads(raw)

        transport = post or send

        def call(path, body):
            result = transport(path, body)
            if (not UUID.fullmatch(result.get("requestId", ""))
                    or result.get("scope") != {"projectId": app_id, "environment": environment}):
                raise ValueError("Scope mismatch")
            return result

        customer = call("customers", {"externalUserId": f"jan:user:{user_id}"})["customer"]["id"]
        if not UUID.fullmatch(customer):
            raise ValueError("Customer response")
        result = call("entitlements/check", {"customerId": customer, "requirement": {
            "internal_feature_id": feature, "quantity": "1", "properties": {}}})["check"]
        if (result.get("kind") != "access" or result.get("internal_feature_id") != feature
                or not isinstance(result.get("allowed"), bool)):
            raise ValueError("Expected access Feature")
        allowed = result["allowed"]
    except Exception:
        raise GenerationAccessError(503, "billing_unavailable") from None
    if not allowed:
        raise GenerationAccessError(402, "plan_required")
