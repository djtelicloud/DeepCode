"""
Smart Project Management System
Handles project organization with title-based mapping, payload hashing, and user choice.
"""

import hashlib
import json
import os
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from utils.path_safety import PathSafetyManager, safe_makedirs, validate_path


@dataclass
class ProjectMetadata:
    """Metadata for a project"""
    title: str
    title_hash: str
    payload_hash: str
    created_at: str
    last_modified: str
    status: str  # "active", "complete", "incomplete", "abandoned"
    version: int
    description: str = ""
    source_type: str = "unknown"  # "url", "file", "text", "directory"
    source_path: str = ""


class SmartProjectManager:
    """Smart project management with hashing, versioning, and user choice"""

    def __init__(self, base_dir: str = "./deepcode_lab/projects/"):
        # Use path safety to ensure we're in the right location
        self.path_safety = PathSafetyManager()
        self.base_dir = self.path_safety.validate_path(base_dir)
        self.metadata_file = os.path.join(self.base_dir, ".project_metadata.json")
        self._ensure_base_structure()

    def _ensure_base_structure(self):
        """Ensure the base directory structure exists"""
        safe_makedirs(self.base_dir, exist_ok=True)

    def _load_metadata(self) -> Dict[str, Dict]:
        """Load project metadata from disk"""
        if not os.path.exists(self.metadata_file):
            return {}

        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_metadata(self, metadata: Dict[str, Dict]):
        """Save project metadata to disk"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except OSError:
            pass  # Fail silently for now

    def _hash_title(self, title: str) -> str:
        """Create a hash for the project title"""
        # Clean title for hashing
        clean_title = re.sub(r'[^\w\s-]', '', title.lower()).strip()
        clean_title = re.sub(r'[-\s]+', '-', clean_title)
        return hashlib.sha256(clean_title.encode('utf-8')).hexdigest()[:16]

    def _hash_payload(self, payload: Union[str, Dict]) -> str:
        """Create a hash for the project payload"""
        if isinstance(payload, dict):
            # Sort keys to ensure consistent hashing
            payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        else:
            payload_str = str(payload)

        return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

    def _is_git_url_payload(self, payload: Union[str, Dict]) -> bool:
        """Check if payload contains a git URL"""
        if isinstance(payload, dict):
            # Check various keys for git URLs
            for key in ['url', 'git_url', 'repo_url', 'source_url', 'path']:
                if key in payload:
                    value = str(payload[key])
                    if 'github.com' in value or 'gitlab.com' in value or '.git' in value:
                        return True
        elif isinstance(payload, str):
            return bool(re.search(r'https://github\.com/[^/]+/[^/]+', payload) or
                       re.search(r'https://gitlab\.com/[^/]+/[^/]+', payload) or
                       payload.endswith('.git'))
        return False

    def _is_external_source(self, payload: Union[str, Dict]) -> bool:
        """Check if payload represents an external source (URL, etc.)"""
        if isinstance(payload, dict):
            # Check for URL-like keys
            url_keys = ['url', 'source_url', 'link', 'href', 'download_url']
            for key in url_keys:
                if key in payload and str(payload[key]).startswith(('http://', 'https://')):
                    return True
        elif isinstance(payload, str):
            return payload.startswith(('http://', 'https://'))
        return False

    def _generate_folder_name(self, title: str, version: int = 1) -> str:
        """Generate folder name from title and version"""
        # Clean title for folder name
        clean_title = re.sub(r'[^\w\s-]', '', title).strip()
        clean_title = re.sub(r'[-\s]+', '-', clean_title)
        clean_title = clean_title[:50]  # Limit length

        if version == 1:
            return clean_title
        else:
            return f"{clean_title}-v{version}"

    def _extract_title_from_payload(self, payload: Union[str, Dict]) -> str:
        """Extract or generate a title from the payload"""
        if isinstance(payload, dict):
            # Try to extract title from various keys
            for key in ['title', 'name', 'paper_title', 'project_name']:
                if key in payload and payload[key]:
                    return str(payload[key])

            # Try to extract from paper_info
            if 'paper_info' in payload and isinstance(payload['paper_info'], dict):
                if 'title' in payload['paper_info']:
                    return str(payload['paper_info']['title'])

            # Use path if available
            if 'path' in payload and payload['path']:
                return os.path.basename(payload['path'])

        # Try to extract from string payload
        if isinstance(payload, str):
            # Check for git URLs first (higher priority)
            git_url_match = re.search(r'https://github\.com/([^/]+/[^/]+)', payload)
            if git_url_match:
                repo_path = git_url_match.group(1)
                return repo_path.replace('/', '-')

            # Check for other URL patterns
            url_match = re.search(r'https?://([^/\s]+)', payload)
            if url_match:
                domain = url_match.group(1)
                # Extract meaningful part from domain
                if 'arxiv.org' in domain:
                    # For arxiv, try to extract paper ID
                    arxiv_match = re.search(r'arxiv\.org/(?:abs|pdf)/([^/\s]+)', payload)
                    if arxiv_match:
                        return f"arxiv-{arxiv_match.group(1)}"
                return f"web-{domain.replace('.', '-')}"

            # Look for title patterns in JSON
            try:
                json_match = re.search(r'\{.*\}', payload, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    if isinstance(parsed, dict):
                        return self._extract_title_from_payload(parsed)
            except json.JSONDecodeError:
                pass

            # Extract from file path patterns
            md_match = re.search(r'`([^`]+\.md)`', payload)
            if md_match:
                return os.path.basename(md_match.group(1))

            # Use first line or truncated content as title
            lines = payload.strip().split('\n')
            if lines:
                title = lines[0][:100]  # First 100 chars
                return re.sub(r'[^\w\s-]', '', title).strip() or "Untitled Project"

        return "Untitled Project"

    def analyze_project_request(self, title: str, payload: Union[str, Dict]) -> Dict:
        """
        Analyze a project request and determine the best course of action.

        Args:
            title: Project title (user provided or extracted)
            payload: Project payload/content

        Returns:
            Dict with analysis results and recommendations
        """
        if not title or title.strip() == "":
            title = self._extract_title_from_payload(payload)

        title = title.strip()
        title_hash = self._hash_title(title)
        payload_hash = self._hash_payload(payload)

        metadata = self._load_metadata()

        # Find existing projects with same title hash
        existing_projects = [
            (folder, meta) for folder, meta in metadata.items()
            if meta.get('title_hash') == title_hash
        ]

        # Find projects with same payload hash
        same_payload_projects = [
            (folder, meta) for folder, meta in metadata.items()
            if meta.get('payload_hash') == payload_hash
        ]

        analysis = {
            "title": title,
            "title_hash": title_hash,
            "payload_hash": payload_hash,
            "existing_title_projects": len(existing_projects),
            "same_payload_projects": len(same_payload_projects),
            "recommendations": [],
            "actions": {}
        }

        if same_payload_projects:
            # Exact same payload exists
            folder, meta = same_payload_projects[0]

            # For git URLs or other external sources, assume continue by default
            is_git_url = self._is_git_url_payload(payload)
            is_external_source = self._is_external_source(payload)

            if is_git_url or is_external_source:
                analysis["recommendations"].append(
                    f"Identical source found: {meta['title']} (same URL/source detected)"
                )
                analysis["actions"]["identical_payload"] = {
                    "folder": folder,
                    "metadata": meta,
                    "action": "continue_existing",  # Always continue for same external source
                    "confidence": "high",
                    "reason": "same_git_url" if is_git_url else "same_external_source"
                }
            else:
                analysis["recommendations"].append(
                    f"Identical payload found in project '{meta['title']}' (folder: {folder})"
                )
                analysis["actions"]["identical_payload"] = {
                    "folder": folder,
                    "metadata": meta,
                    "action": "continue_existing" if meta.get('status') != 'complete' else "use_existing",
                    "confidence": "high",
                    "reason": "identical_content"
                }

        if existing_projects and not same_payload_projects:
            # Same title, different payload - new version
            latest_version = max(meta.get('version', 1) for _, meta in existing_projects)
            analysis["recommendations"].append(
                f"Similar project exists with {len(existing_projects)} version(s). Latest: v{latest_version}"
            )
            analysis["actions"]["new_version"] = {
                "suggested_version": latest_version + 1,
                "existing_versions": [(folder, meta.get('version', 1)) for folder, meta in existing_projects]
            }

        if not existing_projects and not same_payload_projects:
            # Brand new project
            analysis["recommendations"].append("New project - will create fresh version")
            analysis["actions"]["new_project"] = {
                "suggested_version": 1
            }

        return analysis

    def make_intelligent_auto_choice(self, title: str, payload: Union[str, Dict]) -> Dict:
        """
        Make an intelligent automatic choice without user interaction.
        This is the smart fallback when no user input is available.

        Args:
            title: Project title
            payload: Project payload

        Returns:
            Dict with project creation/continuation result
        """
        analysis = self.analyze_project_request(title, payload)

        # Priority 1: Identical payload with high confidence (git URLs, etc.)
        if "identical_payload" in analysis["actions"]:
            action_data = analysis["actions"]["identical_payload"]

            if (action_data.get("confidence") == "high" and
                action_data.get("reason") in ["same_git_url", "same_external_source"]):

                print(f"🤖 Auto-decision: Continuing with identical source")
                return self.create_or_continue_project(title, payload, "auto")

            # For other identical payloads, check status
            meta = action_data["metadata"]
            if meta.get("status") in ["active", "incomplete"]:
                print(f"🤖 Auto-decision: Continuing incomplete work")
                return self.create_or_continue_project(title, payload, "continue")
            else:
                print(f"🤖 Auto-decision: Using existing complete project")
                return self.create_or_continue_project(title, payload, "auto")

        # Priority 2: New version of existing project
        if "new_version" in analysis["actions"]:
            print(f"🤖 Auto-decision: Creating new version of existing project")
            return self.create_or_continue_project(title, payload, "auto")

        # Priority 3: Brand new project
        if "new_project" in analysis["actions"]:
            print(f"🤖 Auto-decision: Creating new project")
            return self.create_or_continue_project(title, payload, "new")

        # Fallback: Create new project
        print(f"🤖 Auto-decision: Fallback to new project creation")
        return self.create_or_continue_project(title, payload, "new")

    def create_or_continue_project(
        self,
        title: str,
        payload: Union[str, Dict],
        user_choice: str = "auto",  # "auto", "new", "continue", "version"
        force_version: Optional[int] = None
    ) -> Dict:
        """
        Create a new project or continue existing one based on analysis and user choice.

        Args:
            title: Project title
            payload: Project payload
            user_choice: User's choice ("auto", "new", "continue", "version")
            force_version: Force a specific version number

        Returns:
            Dict with project information and folder path
        """
        analysis = self.analyze_project_request(title, payload)
        metadata = self._load_metadata()

        title = analysis["title"]
        title_hash = analysis["title_hash"]
        payload_hash = analysis["payload_hash"]

        # Determine action based on user choice and analysis
        if user_choice == "auto":
            if "identical_payload" in analysis["actions"]:
                action_data = analysis["actions"]["identical_payload"]

                # For git URLs or high confidence identical payloads, always continue
                if (action_data.get("confidence") == "high" and
                    action_data.get("reason") in ["same_git_url", "same_external_source"]):
                    print(f"🔄 Auto-continuing with identical source: {action_data['metadata'].get('title', 'Unknown')}")
                    return self._continue_existing_project(action_data["folder"], payload)
                elif action_data["action"] == "continue_existing":
                    print(f"🔄 Auto-continuing existing project: {action_data['metadata'].get('title', 'Unknown')}")
                    return self._continue_existing_project(action_data["folder"], payload)
                else:
                    print(f"✅ Using existing complete project: {action_data['metadata'].get('title', 'Unknown')}")
                    return self._use_existing_project(action_data["folder"])
            elif "new_version" in analysis["actions"]:
                version = analysis["actions"]["new_version"]["suggested_version"]
                print(f"📝 Creating new version v{version} for existing project")
            else:
                version = 1
                print(f"🆕 Creating new project: {title}")
        elif user_choice == "new":
            # Force new version
            if "new_version" in analysis["actions"]:
                version = analysis["actions"]["new_version"]["suggested_version"]
            else:
                version = 1
        elif user_choice == "continue":
            # Try to continue existing incomplete work
            if "identical_payload" in analysis["actions"]:
                action_data = analysis["actions"]["identical_payload"]
                return self._continue_existing_project(action_data["folder"], payload)
            else:
                # No exact match, create new
                version = 1
        elif user_choice == "version":
            version = force_version or 1
        else:
            version = 1

        # Create new project
        folder_name = self._generate_folder_name(title, version)
        folder_path = os.path.join(self.base_dir, folder_name)

        # Ensure unique folder name
        counter = 1
        original_folder_name = folder_name
        while os.path.exists(folder_path):
            folder_name = f"{original_folder_name}-{counter}"
            folder_path = os.path.join(self.base_dir, folder_name)
            counter += 1

        # Validate path safety
        folder_path = self.path_safety.validate_path(folder_path)

        # Create folder safely
        safe_makedirs(folder_path, exist_ok=True)        # Create project metadata
        now = datetime.now().isoformat()
        project_meta = ProjectMetadata(
            title=title,
            title_hash=title_hash,
            payload_hash=payload_hash,
            created_at=now,
            last_modified=now,
            status="active",
            version=version,
            source_type=self._detect_source_type(payload),
            source_path=self._extract_source_path(payload)
        )

        # Save metadata
        metadata[folder_name] = asdict(project_meta)
        self._save_metadata(metadata)

        # Save payload to project
        payload_file = os.path.join(folder_path, ".project_payload.json")
        try:
            with open(payload_file, 'w', encoding='utf-8') as f:
                if isinstance(payload, dict):
                    json.dump(payload, f, indent=2, ensure_ascii=False)
                else:
                    json.dump({"payload": payload}, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

        return {
            "action": "created_new",
            "folder_name": folder_name,
            "folder_path": folder_path,
            "version": version,
            "metadata": asdict(project_meta),
            "analysis": analysis
        }

    def _continue_existing_project(self, folder_name: str, payload: Union[str, Dict]) -> Dict:
        """Continue work on existing project"""
        folder_path = os.path.join(self.base_dir, folder_name)
        metadata = self._load_metadata()

        if folder_name in metadata:
            # Update metadata
            metadata[folder_name]["last_modified"] = datetime.now().isoformat()
            metadata[folder_name]["status"] = "active"
            self._save_metadata(metadata)

            # Clean up any corrupted files
            self._clean_project_directory(folder_path)

        return {
            "action": "continued_existing",
            "folder_name": folder_name,
            "folder_path": folder_path,
            "metadata": metadata.get(folder_name, {})
        }

    def _use_existing_project(self, folder_name: str) -> Dict:
        """Use existing complete project"""
        folder_path = os.path.join(self.base_dir, folder_name)
        metadata = self._load_metadata()

        return {
            "action": "using_existing",
            "folder_name": folder_name,
            "folder_path": folder_path,
            "metadata": metadata.get(folder_name, {})
        }

    def _clean_project_directory(self, folder_path: str):
        """Clean up corrupted or incomplete files in project directory"""
        if not os.path.exists(folder_path):
            return

        files_to_clean = []
        for file_name in os.listdir(folder_path):
            if file_name.startswith('.'):  # Skip hidden files
                continue

            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:  # Empty file
                            files_to_clean.append(file_path)
                except (OSError, UnicodeDecodeError):
                    files_to_clean.append(file_path)  # Corrupted file

        for file_path in files_to_clean:
            try:
                os.remove(file_path)
            except OSError:
                pass

    def _detect_source_type(self, payload: Union[str, Dict]) -> str:
        """Detect the source type from payload"""
        if isinstance(payload, dict):
            return payload.get('input_type', 'unknown')

        if isinstance(payload, str):
            if payload.startswith('http'):
                return 'url'
            elif '.md' in payload or '.pdf' in payload:
                return 'file'
            else:
                return 'text'

        return 'unknown'

    def _extract_source_path(self, payload: Union[str, Dict]) -> str:
        """Extract source path from payload"""
        if isinstance(payload, dict):
            return payload.get('path', '')

        if isinstance(payload, str):
            # Try to extract file path
            md_match = re.search(r'`([^`]+\.[^`]+)`', payload)
            if md_match:
                return md_match.group(1)

        return ''

    def list_projects(self, status_filter: Optional[str] = None) -> Dict:
        """List all projects with their status"""
        metadata = self._load_metadata()
        projects = []

        for folder_name, meta in metadata.items():
            if status_filter and meta.get('status') != status_filter:
                continue

            folder_path = os.path.join(self.base_dir, folder_name)
            projects.append({
                "folder_name": folder_name,
                "folder_path": folder_path,
                "exists": os.path.exists(folder_path),
                **meta
            })

        return {
            "total_projects": len(projects),
            "projects": sorted(projects, key=lambda x: x['last_modified'], reverse=True)
        }

    def update_project_status(self, folder_name: str, status: str, description: str = "") -> bool:
        """Update project status"""
        metadata = self._load_metadata()

        if folder_name not in metadata:
            return False

        metadata[folder_name]["status"] = status
        metadata[folder_name]["last_modified"] = datetime.now().isoformat()

        if description:
            metadata[folder_name]["description"] = description

        self._save_metadata(metadata)
        return True

    def delete_project(self, folder_name: str, confirm: bool = False) -> bool:
        """Delete a project and its folder"""
        if not confirm:
            return False

        metadata = self._load_metadata()
        folder_path = os.path.join(self.base_dir, folder_name)

        # Remove folder
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
            except OSError:
                return False

        # Remove from metadata
        if folder_name in metadata:
            del metadata[folder_name]
            self._save_metadata(metadata)

        return True


# Convenience functions
def smart_project_analysis(title: str, payload: Union[str, Dict], base_dir: str = "./deepcode_lab/projects/") -> Dict:
    """Analyze a project request and get recommendations"""
    manager = SmartProjectManager(base_dir)
    return manager.analyze_project_request(title, payload)


def smart_create_project(
    title: str,
    payload: Union[str, Dict],
    user_choice: str = "auto",
    base_dir: str = "./deepcode_lab/projects/"
) -> Dict:
    """Smart project creation with user choice"""
    manager = SmartProjectManager(base_dir)
    return manager.create_or_continue_project(title, payload, user_choice)
