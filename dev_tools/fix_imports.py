#!/usr/bin/env python3
"""Add missing Optional/Union imports to files that use them"""
import re
from pathlib import Path

def fix_imports(filepath: Path) -> bool:
    """Add Optional/Union to typing imports if they're used but not imported."""
    content = filepath.read_text()
    original = content

    # Check if Optional or Union are used
    uses_optional = 'Optional[' in content
    uses_union = 'Union[' in content

    if not uses_optional and not uses_union:
        return False

    # Check if they're already imported
    has_optional = re.search(r'from typing import.*\bOptional\b', content)
    has_union = re.search(r'from typing import.*\bUnion\b', content)

    needs_optional = uses_optional and not has_optional
    needs_union = uses_union and not has_union

    if not needs_optional and not needs_union:
        return False

    # Find the typing import line
    typing_match = re.search(r'from typing import ([^\n]+)', content), Optional, Union

    if typing_match:
        # Add to existing import
        imports = typing_match.group(1).strip()
        to_add = []
        if needs_optional:
            to_add.append('Optional')
        if needs_union:
            to_add.append('Union')

        new_imports = imports
        for imp in to_add:
            if imp not in new_imports:
                new_imports += f', {imp}'

        content = content.replace(
            typing_match.group(0),
            f'from typing import {new_imports}'
        )
    else:
        # Create new typing import
        to_add = []
        if needs_optional:
            to_add.append('Optional')
        if needs_union:
            to_add.append('Union')

        import_line = f"from typing import {', '.join(to_add)}\n"

        # Insert after __future__ imports or at the top
        future_match = re.search(r'(from __future__ import .*?\n)', content)
        if future_match:
            content = content.replace(future_match.group(0), future_match.group(0) + import_line)
        else:
            # Insert after the first line if it's a shebang or encoding
            lines = content.split('\n')
            insert_at = 0
            if lines and (lines[0].startswith('#!') or 'coding' in lines[0]):
                insert_at = 1
            lines.insert(insert_at, import_line.rstrip())
            content = '\n'.join(lines)

    if content != original:
        filepath.write_text(content)
        return True
    return False

def main():
    py_files = Path('.').rglob('*.py')
    fixed = 0

    for filepath in py_files:
        if '.venv' in str(filepath):
            continue

        try:
            if fix_imports(filepath):
                print(f"Fixed imports in: {filepath}")
                fixed += 1
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")

    print(f"\nFixed {fixed} files")

if __name__ == '__main__':
    main()
