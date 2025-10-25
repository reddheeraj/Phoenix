#!/usr/bin/env python3
"""Test level calculation logic"""

def calculate_level_xp_required(level):
    """Calculate XP required for a specific level"""
    return int(100 * level)

# Simulate what should happen
print("Level Progression Test:")
print("="*60)

current_level = 3
current_xp = 157
total_xp = 457

print(f"Current State:")
print(f"  Level: {current_level}")
print(f"  Current XP: {current_xp}")
print(f"  Total XP: {total_xp}")
print()

print("XP Requirements:")
for i in range(1, 7):
    print(f"  Level {i-1} to Level {i}: {calculate_level_xp_required(i)} XP")
print()

# Simulate adding 50 XP
xp_reward = 50
new_current_xp = current_xp + xp_reward
new_level = current_level
level_ups = 0

print(f"Adding {xp_reward} XP...")
print(f"  New current_xp: {new_current_xp}")
print()

xp_for_next_level = calculate_level_xp_required(new_level + 1)
print(f"  XP needed for level {new_level} to {new_level + 1}: {xp_for_next_level}")
print(f"  Current XP: {new_current_xp}")
print(f"  Can level up? {new_current_xp >= xp_for_next_level}")
print()

while new_current_xp >= xp_for_next_level:
    print(f"  LEVEL UP! {new_level} to {new_level + 1}")
    new_level += 1
    level_ups += 1
    new_current_xp -= xp_for_next_level
    print(f"    Remaining XP after level up: {new_current_xp}")
    xp_for_next_level = calculate_level_xp_required(new_level + 1)
    print(f"    XP needed for next level ({new_level} to {new_level + 1}): {xp_for_next_level}")

print()
print(f"Final State:")
print(f"  New Level: {new_level}")
print(f"  Level Ups: {level_ups}")
print(f"  Remaining Current XP: {new_current_xp}")
print()

# Test the actual progression
print("="*60)
print("Full Progression from Level 0:")
print("="*60)
test_level = 0
test_current_xp = 0

for quest_num in range(1, 20):
    xp_gain = 50
    test_current_xp += xp_gain
    xp_needed = calculate_level_xp_required(test_level + 1)
    
    level_ups_this_quest = 0
    while test_current_xp >= xp_needed:
        test_level += 1
        level_ups_this_quest += 1
        test_current_xp -= xp_needed
        xp_needed = calculate_level_xp_required(test_level + 1)
    
    if level_ups_this_quest > 0:
        print(f"Quest {quest_num}: +{xp_gain} XP -> LEVEL {test_level}! (current XP: {test_current_xp}/{xp_needed})")
    else:
        print(f"Quest {quest_num}: +{xp_gain} XP (Level {test_level}, XP: {test_current_xp}/{xp_needed})")

