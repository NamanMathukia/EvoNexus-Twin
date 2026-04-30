"""
train.py  -- top-level training entrypoint.
Run: python train.py
"""
import os, sys
os.environ["PYTHONUTF8"] = "1"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.models.trainer import train_all

if __name__ == "__main__":
    train_all(n_students=6000, seed=42)
