#!/usr/bin/env python3
"""
Debug script to help identify the file input processing issue
"""

def debug_input_format(input_source):
    """Debug what format the input is in"""
    print(f"🔍 Debugging input: {repr(input_source)}")
    print(f"📋 Type: {type(input_source)}")
    print(f"📏 Length: {len(str(input_source)) if input_source else 0}")

    if isinstance(input_source, str):
        print(f"📄 Content preview: {input_source[:200]}...")
        print(f"🏷️  Starts with: {input_source[:50] if input_source else 'None'}")
        print(f"🏁 Ends with: {input_source[-50:] if len(input_source) > 50 else input_source}")

        # Check if it looks like a file path
        import os
        if os.path.exists(input_source):
            print(f"✅ File/directory exists: {input_source}")
            print(f"📁 Is directory: {os.path.isdir(input_source)}")
            print(f"📄 Is file: {os.path.isfile(input_source)}")
        else:
            print(f"❌ File/directory does not exist: {input_source}")

        # Check if it looks like JSON
        try:
            import json
            parsed = json.loads(input_source)
            print(f"✅ Valid JSON with keys: {list(parsed.keys()) if isinstance(parsed, dict) else 'Not a dict'}")
        except:
            print(f"❌ Not valid JSON")
    else:
        print(f"📋 Non-string input: {input_source}")

if __name__ == "__main__":
    print("🧪 Debug script ready!")
    print("Usage: debug_input_format(your_input_here)")

    # Example usage - you can modify this with your actual input
    # debug_input_format("your_problematic_input_here")
