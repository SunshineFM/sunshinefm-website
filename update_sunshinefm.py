#!/usr/bin/env python3
"""
SunshineFM Episode Article Updater
Replaces article.md files with Local Intelligence versions and commits to GitHub
"""

import os
import subprocess
from pathlib import Path

# Mapping of episode folders to article file names
EPISODES = {
    "Sunday 01-11-2026": "SUN_01-11-2026_article.md",
    "Monday 01-12-2026": "MON_01-12-2026_article.md",
    "Tuesday 01-13-2026": "TUE_01-13-2026_article.md",
    "Wednesday 01-14-2026": "WED_01-14-2026_article.md",
    "Thursday 01-15-2026": "THU_01-15-2026_article.md",
    "Friday 01-16-2026": "FRI_01-16-2026_article.md",
}

# Day names for commit messages
DAY_NAMES = {
    "Sunday 01-11-2026": "Sunday Hello World",
    "Monday 01-12-2026": "Monday Sonic Experiment",
    "Tuesday 01-13-2026": "Tuesday AGI Distraction",
    "Wednesday 01-14-2026": "Wednesday Education Gap",
    "Thursday 01-15-2026": "Thursday Consolidation",
    "Friday 01-16-2026": "Friday Model Wars",
}

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"\n→ {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"  ✓ Success")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error: {e.stderr}")
        raise

def main():
    repo_root = Path.cwd()
    episodes_dir = repo_root / "episodes"
    
    print("=" * 60)
    print("SunshineFM Episode Article Updater")
    print("=" * 60)
    
    # Check we're in the right repo
    if not episodes_dir.exists():
        print("✗ Error: 'episodes' folder not found. Are you in the sunshinefm-website repo?")
        return False
    
    print(f"\n📁 Working in: {repo_root}")
    print(f"📂 Episodes dir: {episodes_dir}")
    
    # Get list of downloaded article files
    downloads_path = Path.home() / "Downloads"
    article_files = {}
    
    print("\n🔍 Looking for article files in ~/Downloads...")
    for episode_folder, article_filename in EPISODES.items():
        local_path = downloads_path / article_filename
        if local_path.exists():
            article_files[episode_folder] = local_path
            print(f"  ✓ Found: {article_filename}")
        else:
            print(f"  ✗ Missing: {article_filename}")
    
    if not article_files:
        print("\n✗ Error: No article files found in ~/Downloads")
        return False
    
    print(f"\n✓ Found {len(article_files)} article files")
    
    # Confirm before proceeding
    response = input("\n⚠️  Ready to update episodes? This will create 6 commits. Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return False
    
    # Update each episode
    updated_count = 0
    for episode_folder, article_path in article_files.items():
        episode_dir = episodes_dir / episode_folder
        target_file = episode_dir / "article.md"
        
        if not episode_dir.exists():
            print(f"\n✗ Episode folder not found: {episode_folder}")
            continue
        
        print(f"\n📝 Processing: {episode_folder}")
        
        # Read the new article content
        with open(article_path, 'r') as f:
            new_content = f.read()
        
        # Write to episode's article.md
        with open(target_file, 'w') as f:
            f.write(new_content)
        print(f"  ✓ Updated {target_file}")
        
        # Stage the file
        run_command(
            f'git add episodes/"{episode_folder}"/article.md',
            f"Staging article.md for {episode_folder}"
        )
        
        # Commit with descriptive message
        day_name = DAY_NAMES.get(episode_folder, episode_folder)
        commit_msg = f"Update: {day_name} article to Local Intelligence format"
        run_command(
            f'git commit -m "{commit_msg}"',
            f"Committing: {commit_msg}"
        )
        
        updated_count += 1
    
    # Push all commits
    if updated_count > 0:
        print(f"\n✓ Updated {updated_count} episodes")
        
        push_response = input(f"\n🚀 Push {updated_count} commits to GitHub? (y/n): ")
        if push_response.lower() == 'y':
            run_command("git push origin main", "Pushing to GitHub")
            print("\n✅ All articles updated and pushed to GitHub!")
        else:
            print(f"\n📌 {updated_count} commits ready to push. Run 'git push origin main' when ready.")
    else:
        print("\n✗ No episodes were updated.")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        exit(1)
