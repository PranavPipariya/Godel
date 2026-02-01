#!/usr/bin/env python3
"""End-to-end test to verify the system is working"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config.config_loader import load_config
from client.api_client import LLMClient
from agent.orchestrator import Agent


async def test_config():
    """Test configuration loading"""
    print("Testing configuration loading...")
    config = load_config(None)

    # Validate config
    errors = config.validate()
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return False

    print("✓ Configuration loaded successfully")
    print(f"  - Model: {config.model_name}")
    print(f"  - API Key: {'Set' if config.api_key else 'Not Set'}")
    print(f"  - Base URL: {config.base_url}")
    print(f"  - Working Directory: {config.cwd}")
    return True


async def test_llm_client():
    """Test LLM client initialization"""
    print("\nTesting LLM client initialization...")
    config = load_config(None)
    client = LLMClient(config)

    try:
        # Just test client initialization
        openai_client = client.get_client()
        print("✓ LLM client initialized successfully")
        await client.close()
        return True
    except Exception as e:
        print(f"❌ LLM client initialization failed: {e}")
        return False


async def test_agent_init():
    """Test agent initialization"""
    print("\nTesting agent initialization...")
    config = load_config(None)

    try:
        async with Agent(config) as agent:
            print("✓ Agent initialized successfully")
            print(f"  - Tools available: {len(agent.session.tool_registry.get_tools())}")
            return True
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Running End-to-End Tests")
    print("=" * 60)

    results = []

    # Test 1: Configuration
    results.append(await test_config())

    # Test 2: LLM Client
    results.append(await test_llm_client())

    # Test 3: Agent Initialization
    results.append(await test_agent_init())

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✓ All tests passed! System is ready.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
