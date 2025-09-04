"""
Path Safety Utilities
Ensures all directory operations stay within the deepcode_lab sandbox.
"""

import os
from pathlib import Path
from typing import Optional


class PathSafetyManager:
    """Ensures all paths stay within the deepcode_lab sandbox"""

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize path safety manager.

        Args:
            project_root: Root project directory (defaults to current working directory)
        """
        if project_root is None:
            project_root = os.getcwd()

        self.project_root = os.path.abspath(project_root)
        self.deepcode_lab_path = os.path.join(self.project_root, "deepcode_lab")

        # Ensure deepcode_lab exists
        os.makedirs(self.deepcode_lab_path, exist_ok=True)

    def validate_path(self, path: str, allow_relative: bool = True) -> str:
        """
        Validate and sanitize a path to ensure it's within deepcode_lab.

        Args:
            path: Path to validate
            allow_relative: Whether to allow relative paths (will be resolved to deepcode_lab)

        Returns:
            str: Validated and safe absolute path

        Raises:
            ValueError: If path is outside deepcode_lab sandbox
        """
        # Convert to absolute path
        if not os.path.isabs(path):
            if allow_relative:
                # Resolve relative paths to deepcode_lab
                if path.startswith("./"):
                    path = path[2:]
                path = os.path.join(self.deepcode_lab_path, path)
            else:
                raise ValueError(f"Relative paths not allowed: {path}")

        # Normalize path
        path = os.path.abspath(path)

        # Ensure path is within deepcode_lab
        if not path.startswith(self.deepcode_lab_path):
            raise ValueError(f"Path outside deepcode_lab sandbox: {path}")

        return path

    def safe_makedirs(self, path: str, exist_ok: bool = True) -> str:
        """
        Safely create directories within deepcode_lab sandbox.

        Args:
            path: Directory path to create
            exist_ok: Whether to ignore if directory already exists

        Returns:
            str: Created directory path
        """
        safe_path = self.validate_path(path)
        os.makedirs(safe_path, exist_ok=exist_ok)
        print(f"✅ Created directory: {safe_path}")
        return safe_path

    def get_safe_project_path(self, project_name: str) -> str:
        """
        Get a safe project path within deepcode_lab/projects/.

        Args:
            project_name: Project name or identifier

        Returns:
            str: Safe project path
        """
        # Clean project name
        import re
        clean_name = re.sub(r'[^\w\s-]', '', str(project_name)).strip()
        clean_name = re.sub(r'[-\s]+', '-', clean_name)

        if not clean_name:
            clean_name = "unnamed-project"

        project_path = os.path.join(self.deepcode_lab_path, "projects", clean_name)
        return self.validate_path(project_path)

    def get_safe_papers_project_path(self, project_name: str, paper_id: str = "1") -> str:
        """
        Get a safe papers project path within deepcode_lab/papers/{project_name}/{id}/.

        Args:
            project_name: Project name or identifier
            paper_id: Paper ID (defaults to "1")

        Returns:
            str: Safe papers project path following papers/{project_name}/{id}/ structure
        """
        # Clean project name
        import re
        clean_name = re.sub(r'[^\w\s-]', '', str(project_name)).strip()
        clean_name = re.sub(r'[-\s]+', '-', clean_name)

        if not clean_name:
            clean_name = "unnamed-project"

        # Clean paper ID
        clean_id = re.sub(r'[^\w\s-]', '', str(paper_id)).strip()
        if not clean_id:
            clean_id = "1"

        papers_project_path = os.path.join(self.deepcode_lab_path, "papers", clean_name, clean_id)
        return self.validate_path(papers_project_path)

    def get_legacy_papers_path(self, paper_id: str) -> str:
        """
        Get a safe legacy papers path for backward compatibility.

        Args:
            paper_id: Paper ID (will be sanitized)

        Returns:
            str: Safe papers path
        """
        # Clean paper ID
        import re
        clean_id = re.sub(r'[^\w\s-]', '', str(paper_id)).strip()

        if not clean_id:
            clean_id = "1"

        papers_path = os.path.join(self.deepcode_lab_path, "papers", clean_id)
        return self.validate_path(papers_path)

    def migrate_external_directory(self, external_path: str) -> Optional[str]:
        """
        Migrate an external directory into deepcode_lab if it exists.

        Args:
            external_path: External directory path

        Returns:
            Optional[str]: New path within deepcode_lab, or None if migration failed
        """
        if not os.path.exists(external_path):
            return None

        # Extract directory name
        dir_name = os.path.basename(external_path)

        # Create safe path
        safe_path = self.get_safe_project_path(f"migrated-{dir_name}")

        try:
            import shutil

            # Move directory
            if os.path.exists(safe_path):
                # If target exists, merge contents
                print(f"🔄 Merging {external_path} into existing {safe_path}")
                for item in os.listdir(external_path):
                    src_item = os.path.join(external_path, item)
                    dst_item = os.path.join(safe_path, item)

                    if os.path.isdir(src_item):
                        if os.path.exists(dst_item):
                            continue  # Skip existing directories
                        shutil.move(src_item, dst_item)
                    else:
                        if not os.path.exists(dst_item):
                            shutil.move(src_item, dst_item)

                # Remove empty source directory
                try:
                    os.rmdir(external_path)
                except OSError:
                    pass
            else:
                # Move entire directory
                print(f"📁 Moving {external_path} to {safe_path}")
                shutil.move(external_path, safe_path)

            return safe_path

        except Exception as e:
            print(f"❌ Failed to migrate {external_path}: {e}")
            return None


# Global instance for easy access
_path_safety = PathSafetyManager()


def safe_makedirs(path: str, exist_ok: bool = True) -> str:
    """Global function for safe directory creation"""
    return _path_safety.safe_makedirs(path, exist_ok)


def validate_path(path: str) -> str:
    """Global function for path validation"""
    return _path_safety.validate_path(path)


def get_safe_project_path(project_name: str) -> str:
    """Global function for safe project paths"""
    return _path_safety.get_safe_project_path(project_name)


def get_safe_papers_project_path(project_name: str, paper_id: str = "1") -> str:
    """Global function for safe papers project paths"""
    return _path_safety.get_safe_papers_project_path(project_name, paper_id)


def migrate_external_directory(external_path: str) -> Optional[str]:
    """Global function for directory migration"""
    return _path_safety.migrate_external_directory(external_path)


def cleanup_external_directories(project_root: Optional[str] = None) -> int:
    """
    Clean up any directories that were created outside deepcode_lab.

    Args:
        project_root: Project root directory

    Returns:
        int: Number of directories migrated
    """
    if project_root is None:
        project_root = os.getcwd()

    migrated_count = 0

    # Look for numeric directories that might be misplaced
    for item in os.listdir(project_root):
        item_path = os.path.join(project_root, item)

        if os.path.isdir(item_path) and item.isdigit():
            # This looks like a misplaced paper directory
            result = migrate_external_directory(item_path)
            if result:
                print(f"✅ Migrated misplaced directory: {item} -> {result}")
                migrated_count += 1

    return migrated_count
