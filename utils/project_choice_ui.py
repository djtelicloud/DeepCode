"""
Project Choice UI Component
Provides interactive prompts for project management decisions.
"""

from typing import Dict, List, Optional, Union

from utils.smart_project_manager import SmartProjectManager


class ProjectChoiceUI:
    """Interactive UI for project management choices"""

    def __init__(self, base_dir: str = "./deepcode_lab/projects/"):
        self.manager = SmartProjectManager(base_dir)

    def present_project_choice(self, title: str, payload: Union[str, Dict]) -> Dict:
        """
        Present project choices to user and get their decision.

        Args:
            title: Project title
            payload: Project payload

        Returns:
            Dict with user choice and project information
        """
        analysis = self.manager.analyze_project_request(title, payload)

        print("\n" + "="*60)
        print(f"🎯 PROJECT ANALYSIS: {analysis['title']}")
        print("="*60)

        print(f"\n📋 Project Details:")
        print(f"   Title: {analysis['title']}")
        print(f"   Title Hash: {analysis['title_hash']}")
        print(f"   Payload Hash: {analysis['payload_hash'][:16]}...")

        # Show recommendations
        print(f"\n💡 Analysis Results:")
        for i, rec in enumerate(analysis['recommendations'], 1):
            print(f"   {i}. {rec}")

        # Present options based on analysis
        options = []

        if "identical_payload" in analysis["actions"]:
            action_data = analysis["actions"]["identical_payload"]
            folder = action_data["folder"]
            meta = action_data["metadata"]
            status = meta.get("status", "unknown")

            print(f"\n🔄 IDENTICAL PAYLOAD DETECTED")
            print(f"   Found in: {folder}")
            print(f"   Status: {status}")
            print(f"   Created: {meta.get('created_at', 'unknown')}")

            if status in ["incomplete", "active"]:
                options.append({
                    "key": "continue",
                    "text": f"Continue existing work in '{folder}'",
                    "recommended": True
                })
            else:
                options.append({
                    "key": "use",
                    "text": f"Use existing complete project '{folder}'",
                    "recommended": True
                })

        if "new_version" in analysis["actions"]:
            version_data = analysis["actions"]["new_version"]
            suggested_version = version_data["suggested_version"]

            print(f"\n📈 VERSION MANAGEMENT")
            print(f"   Existing versions: {len(version_data['existing_versions'])}")
            for folder, version in version_data["existing_versions"]:
                print(f"     - v{version}: {folder}")

            options.append({
                "key": "version",
                "text": f"Create new version (v{suggested_version})",
                "recommended": True
            })

        if "new_project" in analysis["actions"]:
            options.append({
                "key": "new",
                "text": "Create new project (v1)",
                "recommended": True
            })

        # Always offer additional options
        options.extend([
            {
                "key": "force_new",
                "text": "Force create new project (ignore existing)",
                "recommended": False
            },
            {
                "key": "custom_version",
                "text": "Create custom version number",
                "recommended": False
            },
            {
                "key": "list",
                "text": "List all existing projects",
                "recommended": False
            },
            {
                "key": "cancel",
                "text": "Cancel operation",
                "recommended": False
            }
        ])

        return self._get_user_choice(options, analysis)

    def _get_user_choice(self, options: List[Dict], analysis: Dict) -> Dict:
        """Get user choice from options with timeout handling"""
        print(f"\n🎛️  AVAILABLE OPTIONS:")

        recommended_options = [opt for opt in options if opt.get("recommended")]
        other_options = [opt for opt in options if not opt.get("recommended")]

        # Show recommended options first
        if recommended_options:
            print(f"\n   ⭐ RECOMMENDED:")
            for i, option in enumerate(recommended_options, 1):
                print(f"      {i}. {option['text']}")

        if other_options:
            print(f"\n   🔧 OTHER OPTIONS:")
            start_num = len(recommended_options) + 1
            for i, option in enumerate(other_options, start_num):
                print(f"      {i}. {option['text']}")

        # Get user input with timeout
        print(f"\n❓ What would you like to do?")
        print("   Enter choice number (or 'auto' for recommended):")

        import sys
        import threading
        from typing import List as ListType

        user_input: ListType[Optional[str]] = [None]  # Use list to allow modification in nested function

        def get_input():
            try:
                user_input[0] = input("   > ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                user_input[0] = "auto"

        # Start input thread with 30-second timeout
        input_thread = threading.Thread(target=get_input)
        input_thread.daemon = True
        input_thread.start()
        input_thread.join(timeout=30.0)

        choice_text = user_input[0]

        if choice_text is None:
            # Timeout occurred
            print("\n⏰ No response received within 30 seconds.")
            print("   🤖 Agent is making the best choice automatically...")

            # Make intelligent automatic choice
            if recommended_options:
                chosen_option = recommended_options[0]
                print(f"   ✅ Auto-selected: {chosen_option['text']}")
            else:
                chosen_option = options[0]
                print(f"   ✅ Auto-selected: {chosen_option['text']}")
        else:
            # User provided input
            if choice_text == "auto":
                # Use first recommended option
                if recommended_options:
                    chosen_option = recommended_options[0]
                else:
                    chosen_option = options[0]
                print(f"   ✅ Auto-selected: {chosen_option['text']}")
            elif choice_text == "cancel" or choice_text == "c":
                return {"action": "cancelled", "analysis": analysis}
            elif choice_text.isdigit():
                choice_num = int(choice_text)
                if 1 <= choice_num <= len(options):
                    chosen_option = options[choice_num - 1]
                    print(f"   ✅ Selected: {chosen_option['text']}")
                else:
                    print("❌ Invalid choice number. Using auto.")
                    chosen_option = recommended_options[0] if recommended_options else options[0]
                    print(f"   ✅ Auto-selected: {chosen_option['text']}")
            else:
                # Try to match text
                for option in options:
                    if choice_text in option["key"].lower():
                        chosen_option = option
                        print(f"   ✅ Selected: {chosen_option['text']}")
                        break
                else:
                    print("❌ Invalid choice. Using auto.")
                    chosen_option = recommended_options[0] if recommended_options else options[0]
                    print(f"   ✅ Auto-selected: {chosen_option['text']}")

        # Handle the choice
        return self._execute_choice(chosen_option, analysis)

    def _execute_choice(self, option: Dict, analysis: Dict) -> Dict:
        """Execute the user's choice"""
        choice_key = option["key"]
        title = analysis["title"]

        if choice_key == "continue":
            folder = analysis["actions"]["identical_payload"]["folder"]
            result = self.manager._continue_existing_project(folder, {})
            result["user_choice"] = option
            result["analysis"] = analysis
            return result

        elif choice_key == "use":
            folder = analysis["actions"]["identical_payload"]["folder"]
            result = self.manager._use_existing_project(folder)
            result["user_choice"] = option
            result["analysis"] = analysis
            return result

        elif choice_key == "version":
            suggested_version = analysis["actions"]["new_version"]["suggested_version"]
            result = self.manager.create_or_continue_project(
                title, {}, user_choice="version", force_version=suggested_version
            )
            result["user_choice"] = option
            return result

        elif choice_key == "new":
            result = self.manager.create_or_continue_project(title, {}, user_choice="new")
            result["user_choice"] = option
            return result

        elif choice_key == "force_new":
            # Get highest version and increment
            metadata = self.manager._load_metadata()
            title_hash = analysis["title_hash"]
            existing_versions = [
                meta.get("version", 1) for meta in metadata.values()
                if meta.get("title_hash") == title_hash
            ]
            next_version = max(existing_versions) + 1 if existing_versions else 1

            result = self.manager.create_or_continue_project(
                title, {}, user_choice="version", force_version=next_version
            )
            result["user_choice"] = option
            return result

        elif choice_key == "custom_version":
            print("\n🔢 Enter custom version number:")
            version_input = input("   Version: ").strip()
            try:
                custom_version = int(version_input)
                result = self.manager.create_or_continue_project(
                    title, {}, user_choice="version", force_version=custom_version
                )
                result["user_choice"] = option
                return result
            except ValueError:
                print("❌ Invalid version number. Creating v1.")
                result = self.manager.create_or_continue_project(title, {}, user_choice="new")
                result["user_choice"] = option
                return result

        elif choice_key == "list":
            self._show_project_list()
            # After showing list, get choice again
            return self.present_project_choice(title, {})

        elif choice_key == "cancel":
            return {"action": "cancelled", "analysis": analysis}

        else:
            # Default to new
            result = self.manager.create_or_continue_project(title, {}, user_choice="new")
            result["user_choice"] = option
            return result

    def _show_project_list(self):
        """Show list of all projects"""
        projects_data = self.manager.list_projects()

        print(f"\n📂 ALL PROJECTS ({projects_data['total_projects']} total)")
        print("-" * 80)

        if not projects_data["projects"]:
            print("   No projects found.")
            return

        for project in projects_data["projects"]:
            status_emoji = {
                "active": "🔄",
                "complete": "✅",
                "incomplete": "⚠️",
                "abandoned": "❌"
            }.get(project["status"], "❓")

            print(f"   {status_emoji} {project['title']} (v{project['version']})")
            print(f"      📁 {project['folder_name']}")
            print(f"      🕒 {project.get('last_modified', 'unknown')}")
            print(f"      📊 {project['status']}")
            print()

    def ask_for_project_title(self, suggested_title: str = "") -> str:
        """Ask user for project title"""
        print(f"\n📝 PROJECT TITLE")
        print(f"   A descriptive name for your project.")

        if suggested_title:
            print(f"   Suggested: '{suggested_title}'")
            title_input = input("   Enter title (or press Enter to use suggested): ").strip()
            return title_input if title_input else suggested_title
        else:
            while True:
                title_input = input("   Enter project title: ").strip()
                if title_input:
                    return title_input
                print("   ❌ Title cannot be empty.")


def interactive_project_setup(title: str = "", payload: Optional[Union[str, Dict]] = None) -> Dict:
    """
    Interactive project setup with user choices.

    Args:
        title: Optional project title
        payload: Project payload

    Returns:
        Dict with project setup results
    """
    ui = ProjectChoiceUI()

    # Get title if not provided
    if not title:
        suggested_title = ""
        if payload:
            manager = SmartProjectManager()
            suggested_title = manager._extract_title_from_payload(payload)

        title = ui.ask_for_project_title(suggested_title)

    # Present choices and get result
    return ui.present_project_choice(title, payload or {})
