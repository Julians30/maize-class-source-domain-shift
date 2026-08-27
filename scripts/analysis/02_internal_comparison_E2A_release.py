#!/usr/bin/env python3
"""Release entry point. Complete analytical source is stored in audited sequential fragments."""
from pathlib import Path
_BASE = Path(__file__).resolve().parent / "fragments"
_FRAGMENTS = ['02_internal_comparison_E2A_release__part01.py', '02_internal_comparison_E2A_release__part02.py', '02_internal_comparison_E2A_release__part03.py', '02_internal_comparison_E2A_release__part04.py', '02_internal_comparison_E2A_release__part05.py', '02_internal_comparison_E2A_release__part06.py', '02_internal_comparison_E2A_release__part07.py']
for _name in _FRAGMENTS:
    _path = _BASE / _name
    exec(compile(_path.read_text(encoding="utf-8"), str(_path), "exec"), globals())
