#!/usr/bin/env python3
"""
Fix LINE Message Templates Import Issues
แก้ไขปัญหา import ของระบบ Templates
"""

import os
import re

def fix_imports():
    """แก้ไขปัญหา imports ในไฟล์ต่าง ๆ"""
    
    print("🔧 Fixing import issues...")
    
    # Fix main.py - make sure Optional is imported
    main_py_path = "backend/app/main.py"
    if os.path.exists(main_py_path):
        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if Optional is already imported
        if 'from typing import List, Optional' not in content:
            content = content.replace(
                'from typing import List',
                'from typing import List, Optional'
            )
            
            with open(main_py_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Fixed main.py imports")
        else:
            print("✅ main.py imports already correct")
    
    # Fix template_crud.py - make sure Session is imported
    crud_py_path = "backend/app/template_crud.py"
    if os.path.exists(crud_py_path):
        with open(crud_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'from sqlalchemy.orm import Session' not in content:
            # Add Session import at the top
            lines = content.split('\n')
            import_lines = []
            other_lines = []
            
            for line in lines:
                if line.startswith('from sqlalchemy') or line.startswith('import'):
                    import_lines.append(line)
                else:
                    other_lines.append(line)
            
            # Add Session import
            if 'from sqlalchemy.orm import Session' not in '\n'.join(import_lines):
                import_lines.insert(0, 'from sqlalchemy.orm import Session')
            
            content = '\n'.join(import_lines + other_lines)
            
            with open(crud_py_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Fixed template_crud.py imports")
        else:
            print("✅ template_crud.py imports already correct")
    
    # Fix template_selector.py
    selector_py_path = "backend/app/template_selector.py"
    if os.path.exists(selector_py_path):
        with open(selector_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'from sqlalchemy.orm import Session' not in content:
            content = 'from sqlalchemy.orm import Session\n' + content
            
            with open(selector_py_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Fixed template_selector.py imports")
        else:
            print("✅ template_selector.py imports already correct")

if __name__ == "__main__":
    print("🔧 FIXING IMPORT ISSUES")
    print("=" * 40)
    fix_imports()
    print("\n✅ All import issues fixed!")
