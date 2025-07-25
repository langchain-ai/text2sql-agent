#!/usr/bin/env python3
"""
LangGraph API helper script for deployment management.
Handles preview deployments, production deployments, and cleanup.
"""

import argparse
import os
import sys
from typing import Any, Dict, Optional

import requests


class LangGraphAPI:
    """LangGraph API client for deployment management."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        # Use the same endpoint as the working script
        self.base_url = "https://gtm.smith.langchain.dev/api-host/v2"
        # Fix header name to match working script
        self.headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

    def list_deployments(self, name_contains: Optional[str] = None) -> Dict[str, Any]:
        """List deployments with optional name filter."""
        params = {}
        if name_contains:
            params["name_contains"] = name_contains

        response = requests.get(
            f"{self.base_url}/deployments", headers=self.headers, params=params
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to list deployments: {response.status_code}")
            print(f"Response: {response.text}")
            sys.exit(1)

    def create_deployment(
        self, name: str, image_uri: str, openai_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new deployment."""
        # Get OpenAI API key from environment if not provided
        if openai_api_key is None:
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if not openai_api_key:
                print("❌ OPENAI_API_KEY not found in environment variables")
                sys.exit(1)

        # Match the working script structure exactly, but for external_docker
        request_body = {
            "name": name,
            "source": "external_docker",
            "source_config": {
                "integration_id": None,
                "repo_url": None,
                "deployment_type": None,
                "build_on_push": None,
                "custom_url": None,
                "resource_spec": {
                    "min_scale": 1,
                    "max_scale": 1,
                    "cpu": 1,
                    "memory_mb": 1024,
                },
            },
            "source_revision_config": {
                "repo_ref": None,
                "langgraph_config_path": None,
                "image_uri": image_uri,
            },
            "secrets": [
                {
                    "name": "OPENAI_API_KEY",
                    "value": openai_api_key,
                }
            ],
        }

        print(f"📤 Sending deployment request to: {self.base_url}/deployments")
        print(f"📦 Payload: {request_body}")

        response = requests.post(
            f"{self.base_url}/deployments", headers=self.headers, json=request_body
        )

        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")

        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"❌ Failed to create deployment: {response.status_code}")
            print(f"Response: {response.text}")
            print(f"Request URL: {response.url}")
            print(f"Request headers: {dict(response.request.headers)}")
            sys.exit(1)

    def update_deployment(self, deployment_id: str, image_uri: str) -> Dict[str, Any]:
        """Update deployment with new image (creates new revision)."""
        request_body = {
            "source_revision_config": {
                "repo_ref": None,
                "langgraph_config_path": None,
                "image_uri": image_uri,
            }
        }

        print(
            f"📤 Sending update request to: {self.base_url}/deployments/{deployment_id}"
        )
        print(f"📦 Payload: {request_body}")

        response = requests.patch(
            f"{self.base_url}/deployments/{deployment_id}",
            headers=self.headers,
            json=request_body,
        )

        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to update deployment: {response.status_code}")
            print(f"Response: {response.text}")
            print(f"Request URL: {response.url}")
            print(f"Request headers: {dict(response.request.headers)}")
            sys.exit(1)

    def delete_deployment(self, deployment_id: str) -> bool:
        """Delete a deployment."""
        response = requests.delete(
            f"{self.base_url}/deployments/{deployment_id}", headers=self.headers
        )

        if response.status_code == 204:
            return True
        else:
            print(f"❌ Failed to delete deployment: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    def find_deployment_by_name(self, name_contains: str) -> Optional[Dict[str, Any]]:
        """Find a deployment by name pattern."""
        deployments = self.list_deployments(name_contains=name_contains)

        for deployment in deployments.get("resources", []):
            if name_contains in deployment.get("name", ""):
                return deployment

        return None


def deploy_preview(api: LangGraphAPI, pr_number: int, image_uri: str):
    """Deploy or update a preview deployment."""
    deployment_name = f"text2sql-agent-pr-{pr_number}"

    print(f"🔍 Looking for existing preview deployment: {deployment_name}")

    # Check if preview deployment already exists
    existing_deployment = api.find_deployment_by_name(deployment_name)

    if existing_deployment:
        print(f"📝 Found existing preview deployment: {existing_deployment['id']}")
        print(f"🔄 Updating with new image: {image_uri}")

        result = api.update_deployment(existing_deployment["id"], image_uri)
        print("✅ Preview deployment updated successfully!")
        print(f"📦 Deployment ID: {result['id']}")
        print(f"🔗 URL: https://{deployment_name}.langchain.dev")

    else:
        print(f"🆕 Creating new preview deployment: {deployment_name}")
        print(f"📦 Image: {image_uri}")

        result = api.create_deployment(deployment_name, image_uri)
        print("✅ Preview deployment created successfully!")
        print(f"📦 Deployment ID: {result['id']}")
        print(f"🔗 URL: https://{deployment_name}.langchain.dev")


def cleanup_preview(api: LangGraphAPI, pr_number: int):
    """Clean up a preview deployment."""
    deployment_name = f"text2sql-agent-pr-{pr_number}"

    print(f"🔍 Looking for preview deployment to cleanup: {deployment_name}")

    existing_deployment = api.find_deployment_by_name(deployment_name)

    if existing_deployment:
        print(f"🗑️  Deleting preview deployment: {existing_deployment['id']}")

        if api.delete_deployment(existing_deployment["id"]):
            print("✅ Preview deployment deleted successfully!")
        else:
            print("❌ Failed to delete preview deployment")
            sys.exit(1)
    else:
        print(f"ℹ️  No preview deployment found for PR #{pr_number}")


def deploy_production(api: LangGraphAPI, image_uri: str):
    """Deploy or update production deployment."""
    deployment_name = "text2sql-agent-prod"

    print(f"🔍 Looking for production deployment: {deployment_name}")

    existing_deployment = api.find_deployment_by_name(deployment_name)

    if existing_deployment:
        print(f"📝 Found existing production deployment: {existing_deployment['id']}")
        print(f"🔄 Updating with new image: {image_uri}")

        result = api.update_deployment(existing_deployment["id"], image_uri)
        print("✅ Production deployment updated successfully!")
        print(f"📦 Deployment ID: {result['id']}")
        print(f"🔗 URL: https://{deployment_name}.langchain.dev")

    else:
        print(f"🆕 Creating new production deployment: {deployment_name}")
        print(f"📦 Image: {image_uri}")

        result = api.create_deployment(deployment_name, image_uri)
        print("✅ Production deployment created successfully!")
        print(f"📦 Deployment ID: {result['id']}")
        print(f"🔗 URL: https://{deployment_name}.langchain.dev")


def main():
    parser = argparse.ArgumentParser(description="LangGraph API deployment helper")
    parser.add_argument(
        "--action",
        required=True,
        choices=["deploy-preview", "deploy-production", "cleanup-preview"],
        help="Action to perform",
    )
    parser.add_argument("--api-key", required=True, help="LangGraph API key")
    parser.add_argument("--pr-number", type=int, help="PR number (for preview actions)")
    parser.add_argument("--image-uri", help="Docker image URI")
    parser.add_argument(
        "--openai-api-key",
        help="OpenAI API key (optional, will use env var if not provided)",
    )

    args = parser.parse_args()

    api = LangGraphAPI(args.api_key)

    if args.action == "deploy-preview":
        if not args.pr_number or not args.image_uri:
            print("❌ PR number and image URI are required for preview deployment")
            sys.exit(1)
        deploy_preview(api, args.pr_number, args.image_uri)

    elif args.action == "deploy-production":
        if not args.image_uri:
            print("❌ Image URI is required for production deployment")
            sys.exit(1)
        deploy_production(api, args.image_uri)

    elif args.action == "cleanup-preview":
        if not args.pr_number:
            print("❌ PR number is required for preview cleanup")
            sys.exit(1)
        cleanup_preview(api, args.pr_number)


if __name__ == "__main__":
    main()
