#!/usr/bin/env python3
"""
Generate a pretty tree structure of the repository.
This script creates a visual representation of the directory structure,
useful for documentation and project overviews.
"""

import sys
from pathlib import Path


class TreeGenerator:
    """Generate a pretty tree structure of directories and files."""

    # Tree drawing characters
    BRANCH = "├── "
    LAST_BRANCH = "└── "
    TRUNK = "│   "
    SPACE = "    "

    # Default ignore patterns
    DEFAULT_IGNORE = {
        # Version control
        ".git",
        ".gitignore",
        # Python
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        "*.egg-info",
        # Node.js
        "node_modules",
        "npm-debug.log*",
        "yarn-*.log",
        # Build artifacts
        "dist",
        "build",
        "staticfiles",
        # Environment
        ".env",
        ".venv",
        "venv",
        "env",
        # IDE
        ".vscode",
        ".idea",
        "*.swp",
        "*.swo",
        # OS
        ".DS_Store",
        "Thumbs.db",
        # Databases
        "*.sqlite3",
        "db.sqlite3",
    }

    def __init__(
        self,
        root_path: str = ".",
        ignore_patterns: set[str] | None = None,
        max_depth: int | None = None,
        show_hidden: bool = False,
    ):
        """
        Initialize the tree generator.

        Args:
            root_path: Root directory to start from
            ignore_patterns: Set of patterns to ignore (gitignore style)
            max_depth: Maximum depth to traverse (None for unlimited)
            show_hidden: Whether to show hidden files/directories
        """
        self.root_path = Path(root_path).resolve()
        self.ignore_patterns = ignore_patterns or self.DEFAULT_IGNORE
        self.max_depth = max_depth
        self.show_hidden = show_hidden

    def should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored based on patterns."""
        name = path.name

        # Hidden files/directories
        if not self.show_hidden and name.startswith("."):
            return True

        # Check against ignore patterns
        for pattern in self.ignore_patterns:
            if pattern in name or path.match(pattern):
                return True

        return False

    def get_entries(self, directory: Path) -> list[Path]:
        """Get sorted entries from a directory, filtering ignored items."""
        try:
            entries = [
                entry for entry in directory.iterdir() if not self.should_ignore(entry)
            ]
            # Sort: directories first, then files, both alphabetically
            return sorted(entries, key=lambda x: (x.is_file(), x.name.lower()))
        except PermissionError:
            return []

    def generate_tree(
        self,
        directory: Path | None = None,
        prefix: str = "",
        depth: int = 0,
        is_last: bool = True,
    ) -> list[str]:
        """
        Recursively generate tree structure.

        Args:
            directory: Directory to process (defaults to root_path)
            prefix: Current line prefix for tree drawing
            depth: Current depth level
            is_last: Whether this is the last item in its parent

        Returns:
            List of strings representing the tree structure
        """
        if directory is None:
            directory = self.root_path

        tree_lines: list[str] = []

        # Check depth limit
        if self.max_depth is not None and depth > self.max_depth:
            return tree_lines

        entries = self.get_entries(directory)

        for i, entry in enumerate(entries):
            is_last_entry = i == len(entries) - 1

            # Choose appropriate tree characters
            if is_last_entry:
                current_prefix = prefix + self.LAST_BRANCH
                next_prefix = prefix + self.SPACE
            else:
                current_prefix = prefix + self.BRANCH
                next_prefix = prefix + self.TRUNK

            # Add entry name with emoji for type indication
            if entry.is_dir():
                name = f"📁 {entry.name}/"
            else:
                name = f"📄 {entry.name}"

            tree_lines.append(current_prefix + name)

            # Recurse into directories
            if entry.is_dir():
                subtree = self.generate_tree(
                    entry, next_prefix, depth + 1, is_last_entry
                )
                tree_lines.extend(subtree)

        return tree_lines

    def generate_simple_tree(
        self, directory: Path | None = None, prefix: str = "", depth: int = 0
    ) -> list[str]:
        """Generate a simpler tree without emoji decorations."""
        if directory is None:
            directory = self.root_path

        tree_lines: list[str] = []

        if self.max_depth is not None and depth > self.max_depth:
            return tree_lines

        entries = self.get_entries(directory)

        for i, entry in enumerate(entries):
            is_last_entry = i == len(entries) - 1

            if is_last_entry:
                current_prefix = prefix + self.LAST_BRANCH
                next_prefix = prefix + self.SPACE
            else:
                current_prefix = prefix + self.BRANCH
                next_prefix = prefix + self.TRUNK

            # Simple name with trailing slash for directories
            name = entry.name + ("/" if entry.is_dir() else "")
            tree_lines.append(current_prefix + name)

            if entry.is_dir():
                subtree = self.generate_simple_tree(entry, next_prefix, depth + 1)
                tree_lines.extend(subtree)

        return tree_lines


def main():
    """Main function to run the tree generator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a pretty tree structure of the repository"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Root path to generate tree from (default: current directory)",
    )
    parser.add_argument("-d", "--max-depth", type=int, help="Maximum depth to traverse")
    parser.add_argument(
        "-s",
        "--simple",
        action="store_true",
        help="Generate simple tree without emojis",
    )
    parser.add_argument(
        "-a", "--all", action="store_true", help="Show hidden files and directories"
    )
    parser.add_argument("-o", "--output", help="Output file (default: print to stdout)")
    parser.add_argument(
        "--ignore",
        action="append",
        help="Additional patterns to ignore (can be used multiple times)",
    )

    args = parser.parse_args()

    # Build ignore patterns
    ignore_patterns = TreeGenerator.DEFAULT_IGNORE.copy()
    if args.ignore:
        ignore_patterns.update(args.ignore)

    # Create tree generator
    generator = TreeGenerator(
        root_path=args.path,
        ignore_patterns=ignore_patterns,
        max_depth=args.max_depth,
        show_hidden=args.all,
    )

    try:
        # Generate tree
        if args.simple:
            tree_lines = generator.generate_simple_tree()
        else:
            tree_lines = generator.generate_tree()

        # Add header
        root_name = generator.root_path.name or str(generator.root_path)
        if args.simple:
            header = f"{root_name}/"
        else:
            header = f"📁 {root_name}/"

        output_lines = [header] + tree_lines

        # Output
        output_text = "\n".join(output_lines)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_text + "\n")
            print(f"Tree structure written to: {args.output}")
        else:
            print(output_text)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
