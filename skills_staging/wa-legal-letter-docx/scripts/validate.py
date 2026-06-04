#!/usr/bin/env python3
"""
validate.py — Quick structural validation for .docx files.
Part of the wa-legal-letter-docx skill.

Usage:
    python3 validate.py path/to/output.docx
"""

import sys
import zipfile

def validate(path: str) -> bool:
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            required = ['word/document.xml', '[Content_Types].xml']
            missing = [n for n in required if n not in names]
            if missing:
                print(f'FAIL — missing entries: {missing}')
                return False

            xml = z.read('word/document.xml')
            print(f'OK — {path}')
            print(f'     {len(names)} ZIP entries')
            print(f'     document.xml: {len(xml):,} bytes')

            # Check for common docx-js issues
            xml_str = xml.decode('utf-8', errors='replace')
            issues = []
            if 'cantSplit' not in xml_str:
                issues.append('WARNING: no cantSplit found — tables may split across pages')
            if 'w:headerReference' not in xml_str and 'w:header' not in xml_str:
                issues.append('WARNING: no header reference found')
            if 'w:footerReference' not in xml_str and 'w:footer' not in xml_str:
                issues.append('WARNING: no footer reference found')
            if issues:
                for i in issues:
                    print(f'     {i}')
            else:
                print('     All structural checks passed.')
            return True
    except zipfile.BadZipFile:
        print(f'FAIL — not a valid ZIP/DOCX: {path}')
        return False
    except Exception as e:
        print(f'FAIL — {e}')
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 validate.py <file.docx>')
        sys.exit(1)
    ok = validate(sys.argv[1])
    sys.exit(0 if ok else 1)
