#!/usr/bin/env python3
"""
Test script for LangGraph API to verify connection and payload structure.
"""

import os
import sys

from langgraph_api import LangGraphAPI


def test_api_connection():
    """Test basic API connection and list deployments."""
    api_key = os.environ.get("LANGSMITH_API_KEY")
    if not api_key:
        print("❌ LANGSMITH_API_KEY not found in environment")
        return False

    print("🔍 Testing LangGraph API connection...")

    api = LangGraphAPI(api_key)

    try:
        # Test listing deployments
        deployments = api.list_deployments()
        print(
            f"✅ Successfully listed {len(deployments.get('resources', []))} deployments"
        )
        return True
    except Exception as e:
        print(f"❌ Failed to connect to API: {e}")
        return False


def test_payload_structure():
    """Test the payload structure without actually creating a deployment."""
    api_key = os.environ.get("LANGSMITH_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("❌ LANGSMITH_API_KEY not found in environment")
        return False

    if not openai_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False

    print("🔍 Testing payload structure...")

    LangGraphAPI(api_key)

    # Create a test payload (without sending)
    test_name = "test-deployment"
    test_image = "docker.io/test/image:latest"

    payload = {
        "name": test_name,
        "source": "external_docker",
        "source_config": {
            "integration_id": None,
            "repo_url": None,
            "deployment_type": None,
            "build_on_push": None,
            "custom_url": None,
            "resource_spec": None,
        },
        "source_revision_config": {
            "repo_ref": None,
            "langgraph_config_path": None,
            "image_uri": test_image,
        },
        "secrets": [
            {
                "name": "OPENAI_API_KEY",
                "value": openai_key,
            }
        ],
    }

    print("📦 Test payload structure:")
    print(f"   - name: {payload['name']}")
    print(f"   - source: {payload['source']}")
    print(f"   - source_config: {payload['source_config']}")
    print(f"   - source_revision_config: {payload['source_revision_config']}")
    print(f"   - secrets: {len(payload['secrets'])} secret(s)")

    return True


def main():
    """Run all tests."""
    print("🧪 Testing LangGraph API...")

    # Test 1: API Connection
    if not test_api_connection():
        sys.exit(1)

    # Test 2: Payload Structure
    if not test_payload_structure():
        sys.exit(1)

    print("✅ All tests passed!")


if __name__ == "__main__":
    main()
