#!/usr/bin/env python3
"""Fix Python 3.10+ union syntax to be compatible with Python 3.9"""
import re
from pathlib import Path
import sys

def fix_file(filepath: Path) -> bool:
    """Fix union type syntax in a single file. Returns True if changes were made."""
    content = filepath.read_text()
    original = content

    # Track if we need to add Optional import
    needs_optional = False
    needs_union = False

    # Replace Optional[Type] with Optional[Type] in type hints
    # This regex looks for patterns like "Optional[str]" or "Optional[SomeClass]"
    pattern = r'\b([A-Za-z_][\w\.]*(?:\[[\w\[\], ]+\])?)\s*\|\s*None\b'
    if re.search(pattern, content):
        needs_optional = True
        content = re.sub(pattern, r'Optional[\1]', content)

    # Replace patterns like "Type1 | Type2" (but not with None)
    # This is trickier and less common, so we'll be conservative
    complex_union = r'\b([A-Za-z_][\w\.]*(?:\[[\w\[\], ]+\])?)\s*\|\s*([A-Za-z_][\w\.]*(?:\[[\w\[\], ]+\])?)\b'
    if re.search(complex_union, content) and '| None' not in content:
        needs_union = True
        content = re.sub(complex_union, r'Union[\1, \2]', content)

    # Check if imports already exist
    has_optional = 'Optional' in content and ('from typing import' in content or 'import typing' in content)
    has_union = 'Union' in content and ('from typing import' in content or 'import typing' in content)

    # Add imports if needed
    if (needs_optional and not has_optional) or (needs_union and not has_union):
        imports_to_add = []
        if needs_optional and not has_optional:
            imports_to_add.append('Optional')
        if needs_union and not has_union:
            imports_to_add.append('Union')

        # Find existing typing imports
        typing_import_pattern = r'from typing import (.*?)(?:\n|$)', Optional, Union
        match = re.search(typing_import_pattern, content)

        if match:
            # Add to existing import
            existing_imports = match.group(1)
            new_imports = existing_imports.rstrip()
            for imp in imports_to_add:
                if imp not in new_imports:
                    new_imports += f', {imp}'
            content = content.replace(match.group(0), f'from typing import {new_imports}\n')
        else:
            # Add new import after other imports or at the top
            import_line = f"from typing import {', '.join(imports_to_add)}\n"

            # Try to insert after __future__ imports if they exist
            future_pattern = r'(from __future__ import .*?\n)'
            future_match = re.search(future_pattern, content)
            if future_match:
                content = content.replace(future_match.group(0), future_match.group(0) + import_line)
            else:
                # Insert at the beginning
                content = import_line + content

    if content != original:
        filepath.write_text(content)
        return True
    return False

def main():
    # Get all Python files except in .venv
    py_files = Path('.').rglob('*.py')
    fixed_count = 0

    for filepath in py_files:
        if '.venv' in str(filepath):
            continue

        try:
            if fix_file(filepath):
                print(f"Fixed: {filepath}")
                fixed_count += 1
        except Exception as e:
            print(f"Error fixing {filepath}: {e}", file=sys.stderr)

    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()
