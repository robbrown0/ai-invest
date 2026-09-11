#!/usr/local/bin/python3 -I
"""Fixed PAPER web entry; credentials are never command-line input."""
from pathlib import Path
import sys
if len(sys.argv)!=1: raise SystemExit(2)
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'backend'),str(ROOT/'execution')]
from ai_invest_execution.web_gateway import main
raise SystemExit(main())
