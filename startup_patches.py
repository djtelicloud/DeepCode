#!/usr/bin/env python3
"""
Apply all GPT-5 and connection fixes on startup

This script should be imported and run early in your application's lifecycle
to ensure all patches are applied before connections are established.

Usage:
from startup_patches import apply_all_patches
apply_all_patches()  # Call early in startup
"""

import importlib
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def apply_connection_patches():
    """Apply connection safety patches"""
    try:
        # Import the connection safety patch
        from fix_connection_shutdown import initialize as init_conn_safety
        success = init_conn_safety()
        return success
    except ImportError:
        logger.error("Could not import connection safety patch")
        return False
    except Exception as e:
        logger.error(f"Error applying connection safety patch: {e}")
        return False

def apply_gpt5_tool_patches():
    """Apply GPT-5 tool schema patches"""
    try:
        # Check if the patch file exists
        patch_path = Path(__file__).parent / "gpt5_tools_patch.py"
        if not patch_path.exists():
            # Run verification script instead
            import subprocess
            logger.info("Running tool verification script to check for issues...")
            result = subprocess.run([sys.executable, 'verify_gpt5_tools.py'],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning("Tool verification found issues")
                logger.info(result.stdout)
            else:
                logger.info("All tools already valid, no patch needed")
                return True

        # Apply patch if it exists
        if patch_path.exists():
            # Execute the patch file as a subprocess
            import subprocess
            logger.info(f"Applying GPT-5 tool patches from {patch_path}")
            result = subprocess.run([sys.executable, str(patch_path)],
                                    capture_output=True, text=True)
            logger.info(result.stdout)
            return result.returncode == 0

        return True
    except Exception as e:
        logger.error(f"Error applying GPT-5 tool patches: {e}")
        return False

def check_responses_api_compatibility():
    """Check OpenAI client for responses API compatibility"""
    try:
        import openai
        from openai import AsyncOpenAI

        # Check client version
        if not hasattr(openai, "__version__"):
            logger.warning("OpenAI client version unknown - may not support responses API")
            return False

        version = openai.__version__
        logger.info(f"OpenAI client version: {version}")

        # Check for responses API
        test_client = AsyncOpenAI()
        has_responses = hasattr(test_client, "responses")

        if has_responses:
            logger.info("✅ OpenAI client supports responses API")
            return True
        else:
            logger.warning("⚠️ OpenAI client does not support responses API")
            return False

    except ImportError:
        logger.error("Could not import OpenAI client")
        return False
    except Exception as e:
        logger.error(f"Error checking OpenAI client: {e}")
        return False

def apply_all_patches():
    """Apply all patches and fixes"""
    logger.info("🚀 Applying startup patches...")

    # Apply connection patches
    conn_success = apply_connection_patches()
    logger.info(f"Connection patches: {'✅ SUCCESS' if conn_success else '❌ FAILED'}")

    # Apply GPT-5 tool patches
    tool_success = apply_gpt5_tool_patches()
    logger.info(f"GPT-5 tool patches: {'✅ SUCCESS' if tool_success else '❌ FAILED'}")

    # Check OpenAI client
    api_compat = check_responses_api_compatibility()

    # Return overall success
    overall = conn_success and tool_success
    logger.info(f"All patches applied: {'✅ SUCCESS' if overall else '⚠️ PARTIAL SUCCESS or FAILURE'}")

    return overall

if __name__ == "__main__":
    print("="*60)
    print("Startup Patches Utility")
    print("="*60)
    success = apply_all_patches()

    if success:
        print("\n✅ All patches applied successfully!")
    else:
        print("\n⚠️ Some patches could not be applied")
        print("Check the logs for details")

    print("\nTo use these patches in your application:")
    print("from startup_patches import apply_all_patches")
    print("apply_all_patches()  # Call early in startup")
    print("="*60)
