"""
File processing utilities for handling paper files and related operations.
"""

import json
import os
import re
from typing import Dict, List, Optional, Union


class FileProcessor:
    """
    A class to handle file processing operations including path extraction and file reading.
    """

    @staticmethod
    def extract_file_path(file_info: Union[str, Dict]) -> Optional[str]:
        """
        Extract paper directory path from the input information.

        Args:
            file_info: Either a JSON string or a dictionary containing file information

        Returns:
            Optional[str]: The extracted paper directory path or None if not found
        """
        try:
            # Handle direct file path input
            if isinstance(file_info, str):
                # Check if it's a file path (existing or not)
                if file_info.endswith(
                    (".md", ".pdf", ".txt", ".docx", ".doc", ".html", ".htm")
                ):
                    # It's a file path, return the directory
                    return os.path.dirname(os.path.abspath(file_info))
                elif os.path.exists(file_info):
                    if os.path.isfile(file_info):
                        return os.path.dirname(os.path.abspath(file_info))
                    elif os.path.isdir(file_info):
                        return os.path.abspath(file_info)

                # Try to parse as JSON
                try:
                    info_dict = json.loads(file_info)
                except json.JSONDecodeError:
                    # 尝试从文本中提取JSON
                    info_dict = FileProcessor.extract_json_from_text(file_info)
                    if not info_dict:
                        # If not JSON and doesn't look like a file path, raise error
                        raise ValueError(
                            f"Input is neither a valid file path nor JSON: {file_info}"
                        )
            else:
                info_dict = file_info

            # Extract paper path from dictionary
            paper_path = info_dict.get("paper_path")
            if not paper_path:
                raise ValueError("No paper_path found in input dictionary")

            # Get the directory path instead of the file path
            paper_dir = os.path.dirname(paper_path)

            # Convert to absolute path if relative
            if not os.path.isabs(paper_dir):
                paper_dir = os.path.abspath(paper_dir)

            return paper_dir

        except (AttributeError, TypeError) as e:
            raise ValueError(f"Invalid input format: {str(e)}")

    @staticmethod
    def find_markdown_file(directory: str) -> Optional[str]:
        """
        Find the first markdown file in the given directory.

        Args:
            directory: Directory path to search

        Returns:
            Optional[str]: Path to the markdown file or None if not found
        """
        if not os.path.isdir(directory):
            return None

        for file in os.listdir(directory):
            if file.endswith(".md"):
                return os.path.join(directory, file)
        return None

    @staticmethod
    def parse_markdown_sections(content: str) -> List[Dict[str, Union[str, int, List]]]:
        """
        Parse markdown content and organize it by sections based on headers.

        Args:
            content: The markdown content to parse

        Returns:
            List[Dict]: A list of sections, each containing:
                - level: The header level (1-6)
                - title: The section title
                - content: The section content
                - subsections: List of subsections
        """
        # Split content into lines
        lines = content.split("\n")
        sections = []
        current_section = None
        current_content = []

        for line in lines:
            # Check if line is a header
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)

            if header_match:
                # If we were building a section, save its content
                if current_section is not None:
                    current_section["content"] = "\n".join(current_content).strip()
                    sections.append(current_section)

                # Start a new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = {
                    "level": level,
                    "title": title,
                    "content": "",
                    "subsections": [],
                }
                current_content = []
            elif current_section is not None:
                current_content.append(line)

        # Don't forget to save the last section
        if current_section is not None:
            current_section["content"] = "\n".join(current_content).strip()
            sections.append(current_section)

        return FileProcessor._organize_sections(sections)

    @staticmethod
    def _organize_sections(sections: List[Dict]) -> List[Dict]:
        """
        Organize sections into a hierarchical structure based on their levels.

        Args:
            sections: List of sections with their levels

        Returns:
            List[Dict]: Organized hierarchical structure of sections
        """
        result = []
        section_stack = []

        for section in sections:
            while section_stack and section_stack[-1]["level"] >= section["level"]:
                section_stack.pop()

            if section_stack:
                section_stack[-1]["subsections"].append(section)
            else:
                result.append(section)

            section_stack.append(section)

        return result

    @staticmethod
    async def read_file_content(file_path: str) -> str:
        """
        Read the content of a file asynchronously.

        Args:
            file_path: Path to the file to read

        Returns:
            str: The content of the file

        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
        """
        try:
            # Ensure the file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Check if file is actually a PDF by reading the first few bytes
            with open(file_path, "rb") as f:
                header = f.read(8)
                if header.startswith(b"%PDF"):
                    raise IOError(
                        f"File {file_path} is a PDF file, not a text file. Please convert it to markdown format or use PDF processing tools."
                    )

            # Read file content
            # Note: Using async with would be better for large files
            # but for simplicity and compatibility, using regular file reading
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return content

        except UnicodeDecodeError as e:
            raise IOError(
                f"Error reading file {file_path}: File encoding is not UTF-8. Original error: {str(e)}"
            )
        except Exception as e:
            raise IOError(f"Error reading file {file_path}: {str(e)}")

    @staticmethod
    def format_section_content(section: Dict) -> str:
        """
        Format a section's content with standardized spacing and structure.

        Args:
            section: Dictionary containing section information

        Returns:
            str: Formatted section content
        """
        # Start with section title
        formatted = f"\n{'#' * section['level']} {section['title']}\n"

        # Add section content if it exists
        if section["content"]:
            formatted += f"\n{section['content'].strip()}\n"

        # Process subsections
        if section["subsections"]:
            # Add a separator before subsections if there's content
            if section["content"]:
                formatted += "\n---\n"

            # Process each subsection
            for subsection in section["subsections"]:
                formatted += FileProcessor.format_section_content(subsection)

        # Add section separator
        formatted += "\n" + "=" * 80 + "\n"

        return formatted

    @staticmethod
    def standardize_output(sections: List[Dict]) -> str:
        """
        Convert structured sections into a standardized string format.

        Args:
            sections: List of section dictionaries

        Returns:
            str: Standardized string output
        """
        output = []

        # Process each top-level section
        for section in sections:
            output.append(FileProcessor.format_section_content(section))

        # Join all sections with clear separation
        return "\n".join(output)

    @classmethod
    async def process_file_input(
        cls, file_input: Union[str, Dict], base_dir: Optional[str] = None
    ) -> Dict:
        """
        Process file input information and return the structured content.
        Enhanced with smart project management and timeout handling.

        Args:
            file_input: File input information (JSON string, dict, or direct file path)
            base_dir: Optional base directory to use for creating paper directories (for sync support)

        Returns:
            Dict: The structured content with sections and standardized text
        """
        try:
            # Import smart project management and path safety here to avoid circular imports
            from utils.path_safety import (PathSafetyManager, safe_makedirs,
                                           validate_path)
            from utils.project_choice_ui import interactive_project_setup
            from utils.smart_project_manager import SmartProjectManager

            # Initialize path safety
            path_safety = PathSafetyManager()

            # 首先尝试从字符串中提取markdown文件路径
            if isinstance(file_input, str):
                import re

                file_path_match = re.search(r"`([^`]+\.md)`", file_input)
                if file_path_match:
                    paper_path = file_path_match.group(1)
                    file_input = {"paper_path": paper_path}

            # Use smart project management system
            projects_base_dir = "./deepcode_lab/projects/"
            if base_dir:
                projects_base_dir = os.path.join(base_dir, "projects")

            # Validate and ensure safe path
            projects_base_dir = validate_path(projects_base_dir)

            # Extract title from input
            manager = SmartProjectManager(projects_base_dir)
            suggested_title = manager._extract_title_from_payload(file_input)

            # Check if we're in interactive mode (can be set via environment or config)
            interactive_mode = os.getenv("DEEPCODE_INTERACTIVE", "true").lower() == "true"

            project_result = None

            if interactive_mode:
                # Use interactive project setup with timeout handling
                try:
                    project_result = interactive_project_setup(suggested_title, file_input)

                    if project_result.get("action") == "cancelled":
                        # If user cancels, fall back to intelligent auto-choice
                        print("🤖 User cancelled, using intelligent auto-choice...")
                        project_result = manager.make_intelligent_auto_choice(suggested_title, file_input)

                except (KeyboardInterrupt, EOFError, OSError, Exception) as e:
                    # Fall back to intelligent auto-choice if interactive fails
                    print(f"🤖 Interactive mode failed ({type(e).__name__}), using intelligent auto-choice...")
                    project_result = manager.make_intelligent_auto_choice(suggested_title, file_input)

            if not project_result:
                # Use intelligent auto-choice as fallback
                print(f"🤖 Using intelligent auto-choice...")
                project_result = manager.make_intelligent_auto_choice(suggested_title, file_input)

            paper_dir = project_result["folder_path"]
            is_continuing = project_result["action"] in ["continued_existing", "using_existing"]
            project_info = project_result.get("metadata", {})

            print(f"📁 Using project directory: {paper_dir}")

            # Ensure the directory exists safely
            if paper_dir:
                paper_dir = validate_path(paper_dir)
                safe_makedirs(paper_dir, exist_ok=True)

            if not paper_dir:
                raise ValueError("Could not determine paper directory path")

            # Get the actual file path
            file_path = None
            if isinstance(file_input, str):
                # 尝试解析为JSON（处理下载结果）
                try:
                    parsed_json = json.loads(file_input)
                    if isinstance(parsed_json, dict) and "paper_path" in parsed_json:
                        file_path = parsed_json.get("paper_path")
                        # 如果文件不存在，尝试查找markdown文件
                        if file_path and not os.path.exists(file_path):
                            paper_dir_from_path = os.path.dirname(file_path)
                            if os.path.isdir(paper_dir_from_path):
                                file_path = cls.find_markdown_file(paper_dir_from_path)
                                if not file_path:
                                    raise ValueError(
                                        f"No markdown file found in directory: {paper_dir_from_path}"
                                    )
                    else:
                        raise ValueError("Invalid JSON format: missing paper_path")
                except json.JSONDecodeError:
                    # 尝试从文本中提取JSON（处理包含额外文本的下载结果）
                    extracted_json = cls.extract_json_from_text(file_input)
                    if extracted_json and "paper_path" in extracted_json:
                        file_path = extracted_json.get("paper_path")
                        # 如果文件不存在，尝试查找markdown文件
                        if file_path and not os.path.exists(file_path):
                            paper_dir_from_path = os.path.dirname(file_path)
                            if os.path.isdir(paper_dir_from_path):
                                file_path = cls.find_markdown_file(paper_dir_from_path)
                                if not file_path:
                                    raise ValueError(
                                        f"No markdown file found in directory: {paper_dir_from_path}"
                                    )
                    else:
                        # 不是JSON，按文件路径处理
                        # Check if it's a file path (existing or not)
                        if file_input.endswith(
                            (".md", ".pdf", ".txt", ".docx", ".doc", ".html", ".htm")
                        ):
                            if os.path.exists(file_input):
                                file_path = file_input
                            else:
                                # File doesn't exist, try to find markdown in the directory
                                file_path = cls.find_markdown_file(paper_dir)
                                if not file_path:
                                    raise ValueError(
                                        f"No markdown file found in directory: {paper_dir}"
                                    )
                        elif os.path.exists(file_input):
                            if os.path.isfile(file_input):
                                file_path = file_input
                            elif os.path.isdir(file_input):
                                # If it's a directory, find the markdown file
                                file_path = cls.find_markdown_file(file_input)
                                if not file_path:
                                    raise ValueError(
                                        f"No markdown file found in directory: {file_input}"
                                    )
                        else:
                            raise ValueError(f"Invalid input: {file_input}")
            else:
                # Dictionary input
                file_path = file_input.get("paper_path")
                # If the file doesn't exist, try to find markdown in the directory
                if file_path and not os.path.exists(file_path):
                    paper_dir_from_path = os.path.dirname(file_path)
                    if os.path.isdir(paper_dir_from_path):
                        file_path = cls.find_markdown_file(paper_dir_from_path)
                        if not file_path:
                            raise ValueError(
                                f"No markdown file found in directory: {paper_dir_from_path}"
                            )

            if not file_path:
                raise ValueError("No valid file path found")

            # Read file content
            content = await cls.read_file_content(file_path)

            # Parse and structure the content
            structured_content = cls.parse_markdown_sections(content)

            # Generate standardized text output
            standardized_text = cls.standardize_output(structured_content)

            return {
                "paper_dir": paper_dir,
                "file_path": file_path,
                "sections": structured_content,
                "standardized_text": standardized_text,
                "directory_reused": is_continuing,
                "project_info": project_info,
            }

        except Exception as e:
            raise ValueError(f"Error processing file input: {str(e)}")

    @staticmethod
    def extract_json_from_text(text: str) -> Optional[Dict]:
        """
        Extract JSON from text that may contain markdown code blocks or other content.

        Args:
            text: Text that may contain JSON

        Returns:
            Optional[Dict]: Extracted JSON as dictionary or None if not found
        """
        import re

        # Try to find JSON in markdown code blocks
        json_pattern = r"```json\s*(\{.*?\})\s*```"
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find standalone JSON
        json_pattern = r"(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})"
        matches = re.findall(json_pattern, text, re.DOTALL)
        for match in matches:
            try:
                parsed = json.loads(match)
                if isinstance(parsed, dict) and "paper_path" in parsed:
                    return parsed
            except json.JSONDecodeError:
                continue

        return None
