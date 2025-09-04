"""
Smart Project Management System - Simplified Version
Handles project organization with intelligent deduplication and user choice.
"""

import hashlib
import json
import os
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from utils.path_safety import PathSafetyManager, safe_makedirs


@dataclass
class ProjectMetadata:
    """Metadata for a project"""
    title: str
    payload_hash: str
    created_at: str
    last_modified: str
    status: str  # "active", "complete", "incomplete"
    description: str = ""
    source_type: str = "unknown"
    original_payload: str = ""


class SmartProjectManager:
    """Simplified smart project management system"""

    def __init__(self, base_dir: str = "projects"):
        """Initialize with simplified project structure under deepcode_lab/projects/"""
        self.path_safety = PathSafetyManager()
        # Get the deepcode_lab path and append projects
        deepcode_lab = self.path_safety.deepcode_lab_path
        self.base_dir = os.path.join(deepcode_lab, base_dir)
        self.metadata_file = os.path.join(self.base_dir, ".projects.json")
        self._ensure_structure()

    def _ensure_structure(self):
        """Ensure base directory exists"""
        os.makedirs(self.base_dir, exist_ok=True)

    def _load_metadata(self) -> Dict[str, Dict]:
        """Load project metadata"""
        if not os.path.exists(self.metadata_file):
            return {}
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_metadata(self, metadata: Dict[str, Dict]):
        """Save project metadata"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def _hash_payload(self, payload: Union[str, Dict]) -> str:
        """Create hash for payload comparison"""
        if isinstance(payload, dict):
            payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        else:
            payload_str = str(payload).strip()
        return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

    def _extract_project_name(self, payload: Union[str, Dict]) -> str:
        """Extract meaningful project name from payload"""
        if isinstance(payload, dict):
            # Check for obvious title fields
            for key in ['title', 'name', 'project_name']:
                if key in payload and payload[key]:
                    return self._clean_name(str(payload[key]))

            # Check for URL in any field
            for value in payload.values():
                if isinstance(value, str):
                    name = self._extract_from_url(value)
                    if name:
                        return name

        elif isinstance(payload, str):
            # Try to extract from URL first
            name = self._extract_from_url(payload)
            if name:
                return name

            # Use first meaningful line
            lines = payload.strip().split('\n')
            for line in lines:
                clean_line = line.strip()
                if clean_line and len(clean_line) > 3:
                    return self._clean_name(clean_line[:50])

        # Fallback to timestamp
        return f"project-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    def _extract_title_from_payload(self, payload: Union[str, Dict]) -> str:
        """Extract title from payload - alias for _extract_project_name for backwards compatibility"""
        return self._extract_project_name(payload)

    def _extract_from_url(self, text: str) -> Optional[str]:
        """Extract project name from URL"""
        # GitHub URLs
        github_match = re.search(r'github\.com/([^/]+)/([^/\s]+?)(?:\.git|/|$|\s)', text)
        if github_match:
            owner, repo = github_match.groups()
            return f"{owner}-{repo}"

        # Other URLs
        url_match = re.search(r'https?://([^/\s]+)', text)
        if url_match:
            domain = url_match.group(1).replace('www.', '')
            return f"web-{domain.replace('.', '-')}"

        return None

    def _clean_name(self, name: str) -> str:
        """Clean name for use as folder name"""
        clean = re.sub(r'[^\w\s-]', '', name).strip()
        clean = re.sub(r'[-\s]+', '-', clean)
        return clean[:50] or "unnamed"

    def find_matching_projects(self, payload: Union[str, Dict]) -> List[Tuple[str, Dict]]:
        """Find projects that match the given payload"""
        payload_hash = self._hash_payload(payload)
        metadata = self._load_metadata()

        exact_matches = []
        for folder_name, meta in metadata.items():
            if meta.get('payload_hash') == payload_hash:
                exact_matches.append((folder_name, meta))

        return exact_matches

    def create_or_get_project(self, payload: Union[str, Dict], force_new: bool = False) -> Dict:
        """
        Create new project or get existing one based on payload matching.
        This is the main entry point that makes intelligent decisions.
        """
        payload_hash = self._hash_payload(payload)

        # Check for exact matches first
        if not force_new:
            matches = self.find_matching_projects(payload)
            if matches:
                folder_name, metadata = matches[0]
                folder_path = os.path.join(self.base_dir, folder_name)

                # Update last modified
                metadata_dict = self._load_metadata()
                metadata_dict[folder_name]['last_modified'] = datetime.now().isoformat()
                metadata_dict[folder_name]['status'] = 'active'
                self._save_metadata(metadata_dict)

                return {
                    "action": "found_existing",
                    "folder_name": folder_name,
                    "folder_path": folder_path,
                    "metadata": metadata,
                    "message": f"Found existing project with identical content"
                }

        # Create new project
        project_name = self._extract_project_name(payload)
        folder_name = project_name

        # Ensure unique folder name
        counter = 1
        original_name = folder_name
        while os.path.exists(os.path.join(self.base_dir, folder_name)):
            folder_name = f"{original_name}-{counter}"
            counter += 1

        folder_path = os.path.join(self.base_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Create metadata
        now = datetime.now().isoformat()
        project_meta = ProjectMetadata(
            title=project_name,
            payload_hash=payload_hash,
            created_at=now,
            last_modified=now,
            status="active",
            source_type=self._detect_source_type(payload),
            original_payload=str(payload)[:1000]  # Limit size
        )

        # Save metadata
        metadata_dict = self._load_metadata()
        metadata_dict[folder_name] = asdict(project_meta)
        self._save_metadata(metadata_dict)

        # Save payload to project folder
        try:
            payload_file = os.path.join(folder_path, "payload.json")
            with open(payload_file, 'w', encoding='utf-8') as f:
                if isinstance(payload, dict):
                    json.dump(payload, f, indent=2, ensure_ascii=False)
                else:
                    json.dump({"content": payload}, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

        return {
            "action": "created_new",
            "folder_name": folder_name,
            "folder_path": folder_path,
            "metadata": asdict(project_meta),
            "message": f"Created new project: {project_name}"
        }

    def _detect_source_type(self, payload: Union[str, Dict]) -> str:
        """Detect source type"""
        if isinstance(payload, dict):
            return "structured_data"
        elif isinstance(payload, str):
            if payload.startswith(('http://', 'https://')):
                return "url"
            elif any(ext in payload for ext in ['.pdf', '.md', '.txt']):
                return "file"
            else:
                return "text"
        return "unknown"

    def list_projects(self) -> List[Dict]:
        """List all projects"""
        metadata = self._load_metadata()
        projects = []

        for folder_name, meta in metadata.items():
            folder_path = os.path.join(self.base_dir, folder_name)
            projects.append({
                "folder_name": folder_name,
                "folder_path": folder_path,
                "exists": os.path.exists(folder_path),
                **meta
            })

        return sorted(projects, key=lambda x: x['last_modified'], reverse=True)

    def delete_project(self, folder_name: str) -> bool:
        """Delete a project"""
        folder_path = os.path.join(self.base_dir, folder_name)

        # Remove folder
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
            except OSError:
                return False

        # Remove from metadata
        metadata = self._load_metadata()
        if folder_name in metadata:
            del metadata[folder_name]
            self._save_metadata(metadata)

        return True


# Convenience functions
def smart_create_project(payload: Union[str, Dict], force_new: bool = False) -> Dict:
    """Main entry point for smart project creation"""
    manager = SmartProjectManager()
    return manager.create_or_get_project(payload, force_new)


def list_all_projects() -> List[Dict]:
    """List all projects"""
    manager = SmartProjectManager()
    return manager.list_projects()
