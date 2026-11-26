"""flags.py - PHD1 reads its feature flags from Flagsmith.

Run on its own to see the current state of both flags:
    python flags.py
"""

import os

from dotenv import load_dotenv
from flagsmith import Flagsmith

load_dotenv()

# The flag names, exactly as created in the Flagsmith dashboard.
FLAG_BANNER = "phishing_warning_banner"   # low risk: PHD1 may turn it on alone
FLAG_BLOCK_LINKS = "block_external_links"  # high risk: PHD1 must ask a human first


def get_client():
    """Connect to Flagsmith using the server-side key from .env."""
    key = os.getenv("FLAGSMITH_ENVIRONMENT_KEY")
    if not key:
        raise RuntimeError("FLAGSMITH_ENVIRONMENT_KEY is missing from .env")
    return Flagsmith(environment_key=key)


def read_flags(client=None):
    """Return {flag_name: True/False} for both of PHD1's flags."""
    client = client or get_client()
    flags = client.get_environment_flags()
    return {
        FLAG_BANNER: flags.is_feature_enabled(FLAG_BANNER),
        FLAG_BLOCK_LINKS: flags.is_feature_enabled(FLAG_BLOCK_LINKS),
    }


if __name__ == "__main__":
    for name, is_on in read_flags().items():
        print(f"{name}: {'ON' if is_on else 'off'}")
