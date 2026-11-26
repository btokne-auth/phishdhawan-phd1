"""
flag_admin.py - PHD1 switches flags ON through the Flagsmith Admin API.

Reading flags (flags.py) uses the server-side key. CHANGING flags needs a
stronger key: an Organisation API key, kept in .env and never committed.

Check the setup without changing anything:
    python flag_admin.py
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.flagsmith.com/api/v1"                # finding flags
FUTURE_API_URL = "https://api.flagsmith.com/api/__future__"  # changing flags


def _connect():
    """Returns (session, environment_id). Fails loudly if a setting is missing."""
    token = os.getenv("FLAGSMITH_ADMIN_API_KEY")
    environment_id = os.getenv("FLAGSMITH_ENVIRONMENT_ID")
    if not token or not environment_id:
        raise RuntimeError("FLAGSMITH_ADMIN_API_KEY or FLAGSMITH_ENVIRONMENT_ID is missing from .env")
    session = requests.Session()
    session.headers.update({"Authorization": f"Api-Key {token}"})
    return session, environment_id


def find_feature_state(session, environment_id, flag_name):
    """Find the environment-wide state of ONE flag. Refuses to guess: if the
    lookup doesn't return exactly one match, it raises instead of picking one."""
    response = session.get(f"{API_URL}/environments/{environment_id}/featurestates/",
                           params={"feature_name": flag_name}, timeout=15)
    response.raise_for_status()
    results = response.json().get("results", [])
    # Keep only the environment default (not per-user or per-segment overrides).
    matches = [fs for fs in results
               if fs.get("identity") is None and fs.get("feature_segment") is None]
    if len(matches) != 1:
        raise RuntimeError(f"expected 1 feature state for '{flag_name}', found {len(matches)}")
    return matches[0]


def switch_on(flag_name):
    """Switch one flag ON in the environment. Returns True if Flagsmith confirms it."""
    session, environment_id = _connect()
    state = find_feature_state(session, environment_id, flag_name)
    feature = state["feature"]
    feature_id = feature["id"] if isinstance(feature, dict) else feature
    # The old /featurestates/ endpoint is refused (400) on environments with
    # Feature Versioning on, so we use the newer flag-update endpoint, which
    # also records each change as a new version.
    response = session.patch(
        f"{FUTURE_API_URL}/environments/{environment_id}/features/{feature_id}/",
        json={"environment_default": {"enabled": True}}, timeout=15,
    )
    if not response.ok:
        raise RuntimeError(f"Flagsmith said {response.status_code}: {response.text[:200]}")
    return response.json().get("environment_default", {}).get("enabled") is True


if __name__ == "__main__":
    # Read-only check: finds each flag, changes nothing.
    from flags import FLAG_BANNER, FLAG_BLOCK_LINKS
    session, environment_id = _connect()
    for name in (FLAG_BANNER, FLAG_BLOCK_LINKS):
        state = find_feature_state(session, environment_id, name)
        print(f"{name}: found (feature state {state['id']}), "
              f"currently {'ON' if state.get('enabled') else 'off'}")
    print("Admin API setup OK. Nothing was changed.")
