# directory_analyzer.py
"""
Directory analysis script that creates file tree snapshots and extracts
text snippets for AI analysis.
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json

class DirectoryAnalyzer:
    def __init__(self):
        self.readable_extensions = {
            '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml',
            '.yaml', '.yml', '.cfg', '.ini', '.log', '.csv', '.tsv'
        }
        self.max_snippet_length = 500  # Increased from 200 for better analysis
        self.max_files_to_analyze = 25  # Increased from 20
        self.lines_to_extract = 10  # Increased from 5

    def create_file_tree(self, directory: Path, max_depth: int = 3) -> Dict:
        """Create a hierarchical file tree structure."""
        def build_tree(path: Path, current_depth: int = 0) -> Dict:
            if current_depth > max_depth:
                return {"...": "max_depth_reached"}

            tree = {}
            try:
                items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                for item in items:
                    if item.is_dir():
                        tree[f"{item.name}/"] = build_tree(item, current_depth + 1)
                    else:
                        # Include file size and extension info
                        try:
                            size = item.stat().st_size
                            size_str = self.format_file_size(size)
                            tree[item.name] = f"{size_str} | {item.suffix or 'no_ext'}"
                        except:
                            tree[item.name] = "unknown_size"
            except PermissionError:
                tree["[ACCESS_DENIED]"] = "permission_error"

            return tree

        return build_tree(directory)

    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"

    def extract_text_snippets(self, directory: Path, extract_from_end: bool = False) -> Dict[str, str]:
        """Extract brief text snippets from readable files."""
        snippets = {}
        file_count = 0

        for file_path in directory.rglob('*'):
            if file_count >= self.max_files_to_analyze:
                break

            if not file_path.is_file():
                continue

            # Check if file is readable based on extension
            if file_path.suffix.lower() not in self.readable_extensions:
                continue

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                    if extract_from_end:
                        # Extract from the end of the file for retry attempts
                        lines = content.split('\n')
                        if len(lines) > self.lines_to_extract:
                            # Take last N lines
                            relevant_lines = lines[-self.lines_to_extract:]
                        else:
                            relevant_lines = lines
                        snippet = '\n'.join(relevant_lines)[-self.max_snippet_length:]
                        snippet_type = "end"
                    else:
                        # Extract from the beginning (default behavior)
                        lines = content.split('\n')[:self.lines_to_extract]
                        snippet = '\n'.join(lines)[:self.max_snippet_length]
                        snippet_type = "beginning"

                    relative_path = file_path.relative_to(directory)
                    snippets[str(relative_path)] = f"[{snippet_type}] {snippet}"
                    file_count += 1

            except Exception as e:
                # Skip files that can't be read
                continue

        return snippets

    def create_analysis_payload(self, directory: Path, extract_from_end: bool = False) -> Dict:
        """Create the complete analysis payload for AI processing."""
        file_tree = self.create_file_tree(directory)
        text_snippets = self.extract_text_snippets(directory, extract_from_end)

        return {
            "directory_path": str(directory),
            "file_tree": file_tree,
            "text_snippets": text_snippets,
            "analysis_metadata": {
                "total_files_analyzed": len(text_snippets),
                "max_depth": 3,
                "snippet_max_length": self.max_snippet_length,
                "lines_extracted": self.lines_to_extract,
                "extraction_type": "end_of_files" if extract_from_end else "beginning_of_files"
            }
        }

    def create_retry_analysis_payload(self, directory: Path) -> Dict:
        """Create analysis payload for retry attempts, focusing on end of files."""
        print("🔍 Analyzing file endings for more specific context...")
        return self.create_analysis_payload(directory, extract_from_end=True)
