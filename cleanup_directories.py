#!/usr/bin/env python3
"""
Directory Cleanup and Migration Script
Fixes the issue of directories created outside deepcode_lab folder.
"""

import os
import sys

from utils.path_safety import PathSafetyManager, cleanup_external_directories


def main():
    """Main migration function"""
    print("🧹 DIRECTORY CLEANUP AND MIGRATION")
    print("="*50)

    # Get project root (current directory)
    project_root = os.getcwd()
    print(f"📂 Project root: {project_root}")

    # Initialize path safety
    path_safety = PathSafetyManager(project_root)
    print(f"🔒 Deepcode lab path: {path_safety.deepcode_lab_path}")

    print("\n🔍 Scanning for misplaced directories...")

    # Look for problematic directories
    problematic_dirs = []
    for item in os.listdir(project_root):
        item_path = os.path.join(project_root, item)

        if os.path.isdir(item_path):
            # Check if this is a numeric directory (likely misplaced paper folder)
            if item.isdigit():
                problematic_dirs.append((item, item_path, "numeric_paper_folder"))
            # Check for other suspicious patterns
            elif item in ["papers", "projects"] and item_path != path_safety.deepcode_lab_path:
                # These should be inside deepcode_lab
                problematic_dirs.append((item, item_path, "misplaced_structure"))

    if not problematic_dirs:
        print("✅ No problematic directories found!")
        return

    print(f"\n⚠️  Found {len(problematic_dirs)} problematic directories:")
    for i, (name, path, issue_type) in enumerate(problematic_dirs, 1):
        print(f"   {i}. {name} -> {issue_type}")
        print(f"      Path: {path}")

    # Ask for user confirmation
    print(f"\n❓ Do you want to migrate these directories to deepcode_lab?")
    choice = input("   Enter 'y' to migrate, 'n' to skip, 'i' for interactive: ").strip().lower()

    if choice == 'n':
        print("❌ Migration cancelled.")
        return

    migrated_count = 0

    for name, path, issue_type in problematic_dirs:
        if choice == 'i':
            # Interactive mode
            print(f"\n📁 Directory: {name} ({issue_type})")
            migrate_choice = input("   Migrate this directory? (y/n/s=skip all): ").strip().lower()

            if migrate_choice == 's':
                break
            elif migrate_choice != 'y':
                continue

        # Perform migration
        try:
            if issue_type == "numeric_paper_folder":
                # This looks like a paper folder
                new_path = path_safety.get_legacy_papers_path(name)
                print(f"📁 Migrating paper folder: {path} -> {new_path}")

                # Ensure target directory exists
                os.makedirs(os.path.dirname(new_path), exist_ok=True)

                # Move directory
                import shutil
                if os.path.exists(new_path):
                    print(f"   Target exists, merging contents...")
                    # Merge contents
                    for item in os.listdir(path):
                        src_item = os.path.join(path, item)
                        dst_item = os.path.join(new_path, item)

                        if not os.path.exists(dst_item):
                            shutil.move(src_item, dst_item)

                    # Remove empty source
                    try:
                        os.rmdir(path)
                    except OSError:
                        print(f"   Warning: Could not remove source directory (not empty)")
                else:
                    shutil.move(path, new_path)

                migrated_count += 1
                print(f"   ✅ Successfully migrated to: {new_path}")

            elif issue_type == "misplaced_structure":
                # This is a structural folder that should be inside deepcode_lab
                target_path = os.path.join(path_safety.deepcode_lab_path, name)
                print(f"📁 Moving structure folder: {path} -> {target_path}")

                import shutil
                if os.path.exists(target_path):
                    print(f"   Target exists, merging contents...")
                    # Merge contents
                    for item in os.listdir(path):
                        src_item = os.path.join(path, item)
                        dst_item = os.path.join(target_path, item)

                        if os.path.isdir(src_item):
                            if not os.path.exists(dst_item):
                                shutil.move(src_item, dst_item)
                        else:
                            if not os.path.exists(dst_item):
                                shutil.move(src_item, dst_item)

                    # Remove empty source
                    try:
                        os.rmdir(path)
                    except OSError:
                        print(f"   Warning: Could not remove source directory (not empty)")
                else:
                    shutil.move(path, target_path)

                migrated_count += 1
                print(f"   ✅ Successfully moved to: {target_path}")

        except Exception as e:
            print(f"   ❌ Failed to migrate {name}: {e}")

    print(f"\n🎉 Migration complete! Migrated {migrated_count} directories.")

    # Show final structure
    print(f"\n📂 Final deepcode_lab structure:")
    try:
        for root, dirs, files in os.walk(path_safety.deepcode_lab_path):
            level = root.replace(path_safety.deepcode_lab_path, '').count(os.sep)
            indent = '  ' * level
            print(f"{indent}📁 {os.path.basename(root)}/")

            if level < 2:  # Don't go too deep
                sub_indent = '  ' * (level + 1)
                for d in dirs[:5]:  # Show first 5 dirs
                    print(f"{sub_indent}📁 {d}/")
                if len(dirs) > 5:
                    print(f"{sub_indent}... and {len(dirs) - 5} more directories")
    except Exception as e:
        print(f"   Error showing structure: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n❌ Migration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error during migration: {e}")
        sys.exit(1)
