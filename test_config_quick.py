#!/usr/bin/env python3
"""Quick test for config system."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.config import load_config, KenobaseConfig

# Test 1: Default-Konfiguration
print("Test 1: Default Config")
config = KenobaseConfig()
print(f"  Version: {config.version}")
print(f"  Games: {list(config.games.keys())}")

# Test 2: Lade config/default.yaml
print("\nTest 2: Load config/default.yaml")
config2 = load_config("config/default.yaml")
print(f"  Physics enabled: {config2.physics.enable_model_laws}")
print(f"  KENO range: {config2.games['keno'].numbers_range}")

# Test 3: Active Game
print("\nTest 3: Active Game")
game = config2.get_active_game()
print(f"  Name: {game.name}")
print(f"  Numbers: {game.numbers_to_draw}")

print("\n" + "="*40)
print("ALL TESTS PASSED!")
print("="*40)
