#!/usr/bin/env python3
"""Obtain a YouTube OAuth refresh token for GitHub Actions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

from youtube_publish import YOUTUBE_SCOPES


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("client_secret", type=Path, help="OAuth desktop client JSON downloaded from Google Cloud")
    args = parser.parse_args()
    flow = InstalledAppFlow.from_client_secrets_file(str(args.client_secret), YOUTUBE_SCOPES)
    credentials = flow.run_local_server(host="localhost", port=0, access_type="offline", prompt="consent")
    client = json.loads(args.client_secret.read_text(encoding="utf-8")).get("installed", {})
    print("\nStore these values as GitHub Actions secrets:")
    print(f"YOUTUBE_CLIENT_ID={client.get('client_id', '')}")
    print(f"YOUTUBE_CLIENT_SECRET={client.get('client_secret', '')}")
    print(f"YOUTUBE_REFRESH_TOKEN={credentials.refresh_token or ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
