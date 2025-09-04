"""
Workflow Utilities for Error Recovery and Continuation
Provides functions to detect incomplete work and manage workflow continuation.
"""

import json
import os
from typing import Dict, List, Optional, Tuple


class WorkflowRecoveryManager:
    """Manages workflow recovery and continuation logic"""

    def __init__(self, base_papers_dir: str = "./deepcode_lab/papers/"):
        self.base_papers_dir = base_papers_dir

    def scan_for_incomplete_work(self) -> Optional[int]:
        """
        Scan existing directories for incomplete work.

        Returns:
            Optional[int]: Directory ID to continue work in, or None if all work is complete
        """
        if not os.path.exists(self.base_papers_dir):
            return None

        directories = []
        try:
            for item in os.listdir(self.base_papers_dir):
                item_path = os.path.join(self.base_papers_dir, item)
                if os.path.isdir(item_path) and item.isdigit():
                    directories.append(int(item))
        except (OSError, ValueError):
            return None

        if not directories:
            return None

        # Check each directory for completeness, starting with the highest ID
        for dir_id in sorted(directories, reverse=True):
            dir_path = os.path.join(self.base_papers_dir, str(dir_id))
            if self._is_directory_incomplete(dir_path):
                return dir_id

        return None

    def _is_directory_incomplete(self, dir_path: str) -> bool:
        """
        Check if a directory contains incomplete work.

        Args:
            dir_path: Path to the directory to check

        Returns:
            bool: True if directory is incomplete, False if complete
        """
        # Check for required files
        required_files = ["initial_plan.txt", "reference.txt"]

        for file_name in required_files:
            file_path = os.path.join(dir_path, file_name)

            # File missing
            if not os.path.exists(file_path):
                return True

            # File is empty
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        return True
            except (OSError, UnicodeDecodeError):
                return True

        # Check reference.txt for error indicators
        ref_path = os.path.join(dir_path, "reference.txt")
        if os.path.exists(ref_path):
            try:
                with open(ref_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    error_indicators = [
                        "no references found",
                        "error",
                        "failure",
                        "cannot",
                        "unable",
                        "0 references",
                        "no citations"
                    ]
                    if any(indicator in content for indicator in error_indicators):
                        return True
            except (OSError, UnicodeDecodeError):
                pass

        # Check github_download.txt for download failures
        github_path = os.path.join(dir_path, "github_download.txt")
        if os.path.exists(github_path):
            try:
                with open(github_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    failure_indicators = [
                        "can't access",
                        "unable to download",
                        "failed to download",
                        "error downloading",
                        "connection error",
                        "network error"
                    ]
                    if any(indicator in content for indicator in failure_indicators):
                        return True
            except (OSError, UnicodeDecodeError):
                pass

        # Check for actual paper content (.md file)
        has_paper_content = False
        try:
            for item in os.listdir(dir_path):
                if item.endswith('.md') and os.path.isfile(os.path.join(dir_path, item)):
                    # Check if the .md file has substantial content
                    md_path = os.path.join(dir_path, item)
                    with open(md_path, 'r', encoding='utf-8') as f:
                        md_content = f.read().strip()
                        if len(md_content) > 100:  # Arbitrary threshold for "substantial content"
                            has_paper_content = True
                            break
        except (OSError, UnicodeDecodeError):
            pass

        if not has_paper_content:
            return True

        # All checks passed, directory appears complete
        return False

    def get_next_available_id(self) -> int:
        """
        Get the next available ID for a new directory.

        Returns:
            int: Next available directory ID
        """
        # First check if we should continue existing work
        incomplete_id = self.scan_for_incomplete_work()
        if incomplete_id is not None:
            return incomplete_id

        # If no incomplete work, find next available ID
        if not os.path.exists(self.base_papers_dir):
            os.makedirs(self.base_papers_dir, exist_ok=True)
            return 1

        max_id = 0
        try:
            for item in os.listdir(self.base_papers_dir):
                item_path = os.path.join(self.base_papers_dir, item)
                if os.path.isdir(item_path) and item.isdigit():
                    max_id = max(max_id, int(item))
        except (OSError, ValueError):
            pass

        return max_id + 1

    def clean_incomplete_directory(self, dir_id: int) -> bool:
        """
        Clean up corrupted or incomplete files in a directory.

        Args:
            dir_id: Directory ID to clean

        Returns:
            bool: True if cleaning was successful
        """
        dir_path = os.path.join(self.base_papers_dir, str(dir_id))

        if not os.path.exists(dir_path):
            return False

        files_to_clean = []

        # Check for empty or corrupted files
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)

            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:  # Empty file
                            files_to_clean.append(file_path)
                except (OSError, UnicodeDecodeError):
                    files_to_clean.append(file_path)  # Corrupted file

        # Remove corrupted/empty files
        for file_path in files_to_clean:
            try:
                os.remove(file_path)
            except OSError:
                pass

        return True

    def get_directory_status_report(self) -> Dict:
        """
        Get a comprehensive report on all directories and their status.

        Returns:
            Dict: Status report with complete and incomplete directories
        """
        if not os.path.exists(self.base_papers_dir):
            return {
                "total_directories": 0,
                "complete_directories": [],
                "incomplete_directories": [],
                "next_recommended_id": 1,
                "should_continue_existing": False
            }

        directories = []
        try:
            for item in os.listdir(self.base_papers_dir):
                item_path = os.path.join(self.base_papers_dir, item)
                if os.path.isdir(item_path) and item.isdigit():
                    directories.append(int(item))
        except (OSError, ValueError):
            directories = []

        complete_dirs = []
        incomplete_dirs = []

        for dir_id in sorted(directories):
            dir_path = os.path.join(self.base_papers_dir, str(dir_id))
            if self._is_directory_incomplete(dir_path):
                incomplete_dirs.append(dir_id)
            else:
                complete_dirs.append(dir_id)

        next_id = self.get_next_available_id()
        should_continue = next_id in incomplete_dirs

        return {
            "total_directories": len(directories),
            "complete_directories": complete_dirs,
            "incomplete_directories": incomplete_dirs,
            "next_recommended_id": next_id,
            "should_continue_existing": should_continue
        }


# Convenience functions for easy import
def scan_for_incomplete_work(base_dir: str = "./deepcode_lab/papers/") -> Optional[int]:
    """Scan for incomplete work and return directory ID to continue"""
    manager = WorkflowRecoveryManager(base_dir)
    return manager.scan_for_incomplete_work()


def get_next_workflow_id(base_dir: str = "./deepcode_lab/papers/") -> int:
    """Get next ID for workflow, prioritizing incomplete work"""
    manager = WorkflowRecoveryManager(base_dir)
    return manager.get_next_available_id()


def get_workflow_status_report(base_dir: str = "./deepcode_lab/papers/") -> Dict:
    """Get comprehensive status report of all workflows"""
    manager = WorkflowRecoveryManager(base_dir)
    return manager.get_directory_status_report()
