#!/usr/bin/env python3
"""
Smart Project Manager Demo
Demonstrates the new intelligent project management system.
"""

import json

from utils.project_choice_ui import interactive_project_setup
from utils.smart_project_manager import (SmartProjectManager,
                                         smart_project_analysis)


def demo_smart_project_system():
    """Demonstrate the smart project management system"""
    print("🚀 SMART PROJECT MANAGER DEMO")
    print("="*50)

    # Example payloads
    payloads = [
        {
            "title": "Attention Mechanism Research",
            "input_type": "url",
            "path": "https://arxiv.org/abs/1706.03762",
            "paper_info": {
                "title": "Attention Is All You Need",
                "authors": ["Ashish Vaswani", "Noam Shazeer"],
                "year": "2017"
            }
        },
        {
            "title": "Attention Mechanism Research",  # Same title
            "input_type": "file",
            "path": "./papers/transformer_improvements.pdf",
            "paper_info": {
                "title": "Transformer Improvements Study",
                "authors": ["Jane Doe"],
                "year": "2023"
            }
        },
        {
            "title": "Attention Mechanism Research",  # Same title, same payload as first
            "input_type": "url",
            "path": "https://arxiv.org/abs/1706.03762",
            "paper_info": {
                "title": "Attention Is All You Need",
                "authors": ["Ashish Vaswani", "Noam Shazeer"],
                "year": "2017"
            }
        }
    ]

    manager = SmartProjectManager("./demo_projects/")

    print("\n1️⃣ ANALYZING DIFFERENT SCENARIOS\n")

    for i, payload in enumerate(payloads, 1):
        print(f"--- Scenario {i} ---")
        analysis = manager.analyze_project_request(payload["title"], payload)

        print(f"Title: {analysis['title']}")
        print(f"Payload Hash: {analysis['payload_hash'][:16]}...")
        print("Recommendations:")
        for rec in analysis['recommendations']:
            print(f"  • {rec}")

        print("Available Actions:")
        for action_key, action_data in analysis['actions'].items():
            print(f"  • {action_key}: {action_data}")
        print()

    print("\n2️⃣ TESTING PROJECT CREATION\n")

    # Test 1: Create first project
    result1 = manager.create_or_continue_project(
        "Attention Mechanism Research",
        payloads[0],
        user_choice="auto"
    )
    print(f"Result 1: {result1['action']} -> {result1['folder_name']}")

    # Test 2: Try same title, different payload (should suggest version)
    result2 = manager.create_or_continue_project(
        "Attention Mechanism Research",
        payloads[1],
        user_choice="auto"
    )
    print(f"Result 2: {result2['action']} -> {result2['folder_name']}")

    # Test 3: Try identical payload (should continue existing)
    result3 = manager.create_or_continue_project(
        "Attention Mechanism Research",
        payloads[0],
        user_choice="auto"
    )
    print(f"Result 3: {result3['action']} -> {result3['folder_name']}")

    print("\n3️⃣ PROJECT LISTING\n")

    projects_list = manager.list_projects()
    print(f"Total Projects: {projects_list['total_projects']}")

    for project in projects_list['projects']:
        print(f"  📁 {project['title']} (v{project['version']})")
        print(f"     Status: {project['status']}")
        print(f"     Folder: {project['folder_name']}")
        print(f"     Hash: {project['payload_hash'][:16]}...")
        print()

    print("✅ Demo completed!")
    return projects_list


def demo_interactive_ui():
    """Demonstrate the interactive UI"""
    print("\n🎛️ INTERACTIVE UI DEMO")
    print("="*50)

    # Example scenario with conflict
    payload = {
        "title": "GPT-4 Architecture Study",
        "input_type": "url",
        "path": "https://example.com/gpt4-paper.pdf"
    }

    print("This will demonstrate the interactive project choice UI.")
    print("You'll be presented with options for handling the project.")
    print("\nStarting interactive setup...")

    try:
        result = interactive_project_setup("GPT-4 Architecture Study", payload)
        print(f"\n✅ Interactive setup result:")
        print(f"   Action: {result.get('action', 'unknown')}")
        print(f"   Folder: {result.get('folder_name', 'unknown')}")

        if 'user_choice' in result:
            print(f"   User Choice: {result['user_choice']['text']}")

    except KeyboardInterrupt:
        print("\n❌ Demo cancelled by user.")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")


if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. Automated system demo")
    print("2. Interactive UI demo")
    print("3. Both")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice in ["1", "3"]:
        demo_smart_project_system()

    if choice in ["2", "3"]:
        demo_interactive_ui()

    print("\n🎉 All demos completed!")
