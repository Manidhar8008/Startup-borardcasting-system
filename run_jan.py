#!/usr/bin/env python
"""
run_jan.py — Entry point for the JAN AI Broadcasting Assistant.

Usage:
    python run_jan.py                     # Default brand: janani_ai
    python run_jan.py --brand mw_ai_news  # Specify a brand
"""
import argparse
import sys
import os

# Ensure the project root is on the path so all modules resolve correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from ui.chat_interface import run


def parse_args():
    parser = argparse.ArgumentParser(description="JAN — AI Broadcasting Assistant")
    parser.add_argument(
        "--brand",
        default="janani_ai",
        help="Active brand (default: janani_ai)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    load_dotenv()
    args = parse_args()
    run(brand=args.brand)
