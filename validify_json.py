"""
Code for validating the json code generated, attempting to catch any specific errors
"""

import json
from collections import defaultdict

def validate_json(file_path):
    print(f"🔍 - Validating JSON file: {file_path}...\n")

    # Load the JSON file
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"❌ - Failed to parse JSON file: {e}\n")
        return

    # Initialize tracking variables and error counters
    invalid_items = []
    duplicate_asset_ids = set()
    all_asset_ids = set()

    parent_count = defaultdict(int)
    child_count = defaultdict(int)

    blocks = {}

    # Validate each target
    for target_index, target in enumerate(data.get("targets", []), start=1):
        print(f"🔎 - Validating target #{target_index}...\n")

        # Check for duplicate asset IDs in costumes and sounds
        for costume in target.get("costumes", []):
            asset_id = costume.get("assetId", "")
            if not asset_id:
                print(f"❌ - Costume missing assetId in target #{target_index}\n")
                invalid_items.append(costume)
                continue
            if asset_id in all_asset_ids:
                print(f"❌ - Duplicate assetId found: [{asset_id}] in target #{target_index}\n")
                duplicate_asset_ids.add(asset_id)
            all_asset_ids.add(asset_id)

        for sound in target.get("sounds", []):
            asset_id = sound.get("assetId", "")
            if not asset_id:
                print(f"❌ - Sound missing assetId in target #{target_index}\n")
                invalid_items.append(sound)
                continue
            if asset_id in all_asset_ids:
                print(f"❌ - Duplicate assetId found: [{asset_id}] in target #{target_index}\n")
                duplicate_asset_ids.add(asset_id)
            all_asset_ids.add(asset_id)

        # Check blocks for parenting issues
        for block_id, block in target.get("blocks", {}).items():
            blocks[block_id] = block
            parent = block.get("parent")
            next_block = block.get("next")

            if parent:
                parent_count[parent] += 1
            if next_block:
                child_count[block_id] += 1

    # Analyze block relationships
    for block_id, count in parent_count.items():
        if count > 1:
            print(f"❌ - Block [{block_id}] has multiple parents ({count}).\n")
            invalid_items.append(block_id)

    for block_id, count in child_count.items():
        if count > 1:
            print(f"❌ - Block [{block_id}] has multiple children ({count}).\n")
            invalid_items.append(block_id)

    # Check for orphaned blocks or dangling references
    for block_id, block in blocks.items():
        parent = block.get("parent")
        if parent and parent not in blocks:
            print(f"❌ - Block [{block_id}] references non-existent parent [{parent}].\n")
            invalid_items.append(block_id)

        next_block = block.get("next")
        if next_block and next_block not in blocks:
            print(f"❌ - Block [{block_id}] references non-existent next block [{next_block}].\n")
            invalid_items.append(block_id)

    # Final summary
    if duplicate_asset_ids:
        print(f"\n❌ - [{len(duplicate_asset_ids)}] duplicate assetId(s) found.")
    if invalid_items:
        print(f"❌ - [{len(invalid_items)}] total invalid items found. See above for details.\n")
        raise ValueError(f"JSON file validation failed with {len(invalid_items)} errors.")
    else:
        print("✅ - JSON file is valid.\n")

# validate_json("path/to/your/json_file.json")
