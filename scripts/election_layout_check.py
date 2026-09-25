"""election_layout_check — RETIRED 2026-09-24 (build-seq P1, THE MERGE).

main.html is a redirect now; the Elect page lives in mission.html and its 16
assertions grew into `scripts/mission_layout_check.py`. This stub runs that
check so anything still calling the old name gets the real answer. It is in
the removal register (INSTRUCTIONS, "Added 2026-09-24").
"""
import os, runpy
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mission_layout_check.py'), run_name='__main__')
