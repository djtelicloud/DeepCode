#!/usr/bin/env python3
"""
Fix Connection Shutdown Issues
This script adds a safety mechanism to prevent connection closure issues in the MCP framework.

The issue:
- When the aggregator is closing, it's shutting down persistent connections
- But there might still be pending tool calls that need those connections
- This causes "Connection closed" errors

This script:
1. Adds a safety delay before closing connections
2. Provides a monkey-patch utility to apply at runtime
3. Creates an initialization function to apply early in the startup process
"""

import asyncio
import importlib
import inspect
import logging
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Set

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafetyDelayPatch:
    """Connection safety patch for MCP framework"""

    original_functions = {}  # Store original functions to restore if needed

    @staticmethod
    async def patched_connection_close(original_func, self, *args, **kwargs):
        """
        Patched connection close function that adds safety delay
        """
        logger.info("🔒 SafetyDelayPatch: Adding safety delay before connection close...")

        # Add a safety delay to allow pending requests to complete
        await asyncio.sleep(1)

        # Call original close function
        return await original_func(self, *args, **kwargs)

    @staticmethod
    def patch_module_function(module_name: str, function_name: str,
                             wrapper_func: Callable) -> bool:
        """
        Patch a function in a module with a wrapper function

        Args:
            module_name: Name of the module containing the function
            function_name: Name of the function to patch
            wrapper_func: Wrapper function to apply

        Returns:
            bool: True if patching was successful, False otherwise
        """
        try:
            # Import the module
            module = importlib.import_module(module_name)

            # Get the original function
            if hasattr(module, function_name):
                original_func = getattr(module, function_name)

                # Save the original function
                SafetyDelayPatch.original_functions[(module_name, function_name)] = original_func

                # Create the patched function
                async def patched_func(*args, **kwargs):
                    return await wrapper_func(original_func, *args, **kwargs)

                # Apply the patch
                setattr(module, function_name, patched_func)
                logger.info(f"✅ Successfully patched {module_name}.{function_name}")
                return True
            else:
                logger.error(f"❌ Function {function_name} not found in {module_name}")
                return False

        except ImportError:
            logger.error(f"❌ Could not import module {module_name}")
            return False
        except Exception as e:
            logger.error(f"❌ Error patching {module_name}.{function_name}: {e}")
            return False

    @staticmethod
    def add_connection_close_safety():
        """
        Add safety mechanism to prevent connection closure issues

        Returns:
            bool: True if all patches were applied successfully, False otherwise
        """
        # Target module and function for patching
        patches = [
            ("mcp_agent.mcp.mcp_connection_manager", "disconnect_all_persistent"),
            ("mcp_agent.mcp.mcp_server_connection", "close")
        ]

        success = True
        for module_name, function_name in patches:
            result = SafetyDelayPatch.patch_module_function(
                module_name,
                function_name,
                SafetyDelayPatch.patched_connection_close
            )
            success = success and result

        return success

def initialize():
    """Initialize safety patches early in the startup process"""
    logger.info("🔧 Initializing connection safety patches...")
    success = SafetyDelayPatch.add_connection_close_safety()
    if success:
        logger.info("✅ Connection safety patches initialized successfully")
    else:
        logger.warning("⚠️ Some connection safety patches could not be applied")
    return success

def main():
    """Main function to apply patches"""
    print("=" * 60)
    print("MCP Connection Safety Patch Utility")
    print("=" * 60)

    success = SafetyDelayPatch.add_connection_close_safety()

    if success:
        print("✅ Safety patches applied successfully!")
        print("Connection manager will now wait before closing connections")
    else:
        print("⚠️ Some patches could not be applied")
        print("Please check the logs for details")

    print("\n📋 Usage in your code:")
    print("from fix_connection_shutdown import initialize")
    print("initialize()  # Call this early in your startup process")
    print("=" * 60)

if __name__ == "__main__":
    main()
