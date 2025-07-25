#!/usr/bin/env python3
"""
Simple script to list all deployments for testing.
"""

import os
import sys

from langgraph_api import LangGraphAPI


def main():
    """List all deployments."""
    api_key = os.environ.get("LANGSMITH_API_KEY")
    if not api_key:
        print("❌ LANGSMITH_API_KEY not found in environment")
        sys.exit(1)

    api = LangGraphAPI(api_key)

    try:
        deployments = api.list_deployments()
        print(f"📋 Found {len(deployments.get('resources', []))} deployments:")
        print()

        for deployment in deployments.get("resources", []):
            name = deployment.get("name", "Unknown")
            status = deployment.get("status", "Unknown")
            deployment_id = deployment.get("id", "Unknown")
            created_at = deployment.get("created_at", "Unknown")

            print(f"🔗 **{name}**")
            print(f"   Status: {status}")
            print(f"   ID: {deployment_id}")
            print(f"   Created: {created_at}")
            print()

    except Exception as e:
        print(f"❌ Error listing deployments: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
