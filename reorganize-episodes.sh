#!/bin/bash
set -e

echo "🚀 SunshineFM Episode Reorganization (Full Cleanup)"
echo "===================================================="

REPO="/Users/macmini/sunshinefm-website"
cd "$REPO"

# 1. Create clean directory structure
echo "📁 Step 1: Creating clean directory structure..."
mkdir -p "$REPO/episodes/2026/january"
mkdir -p "$REPO/episodes/2026/february"

# 2. Migrate content from old locations
echo "📦 Step 2: Migrating episodes to clean structure..."

# Map old folders to ISO dates
declare -A EPISODE_MAP=(
    ["Sunday 01-11-2026"]="2026-01-11"
    ["Monday 01-12-2026"]="2026-01-12"
    ["Tuesday 01-13-2026"]="2026-01-13"
    ["Wednesday 01-14-2026"]="2026-01-14"
    ["Thursday 01-15-2026"]="2026-01-15"
    ["Friday 01-16-2026"]="2026-01-16"
    ["Monday 01-19-2026"]="2026-01-19"
    ["Tuesday 01-20-2026"]="2026-01-20"
    ["Wednesday 01-21-2026"]="2026-01-21"
    ["Thursday 01-22-2026"]="2026-01-22"
    ["Friday 01-23-2026"]="2026-01-23"
)

# For each old episode folder, create new structure
for old_folder in "$REPO/episodes"/*/; do
    if [ -d "$old_folder" ] && [ ! "$old_folder" == "$REPO/episodes/2026/" ]; then
        folder_name=$(basename "$old_folder")
        
        # Skip if it's a number/date folder already
        if [[ ! "$folder_name" =~ ^[0-9] ]]; then
            iso_date="${EPISODE_MAP[$folder_name]}"
            
            if [ -n "$iso_date" ]; then
                # Create the new episode folder
                new_folder="$REPO/episodes/2026/january/$iso_date"
                mkdir -p "$new_folder"
                
                # Copy article.md and transcript.md if they exist
                [ -f "$old_folder/article.md" ] && cp "$old_folder/article.md" "$new_folder/"
                [ -f "$old_folder/transcript.md" ] && cp "$old_folder/transcript.md" "$new_folder/"
                
                echo "  ✓ Migrated: $folder_name → 2026-01-XX/$iso_date"
            fi
        fi
    fi
done

# Also pull in content from local-intelligence if it's different
echo "📝 Step 2b: Cross-referencing local-intelligence content..."
for li_file in "$REPO/local-intelligence/2026/january"/*.md; do
    if [ -f "$li_file" ]; then
        filename=$(basename "$li_file")
        iso_date="${filename:0:10}"  # Extract YYYY-MM-DD
        
        if [ ! -f "$REPO/episodes/2026/january/$iso_date/article.md" ]; then
            mkdir -p "$REPO/episodes/2026/january/$iso_date"
            cp "$li_file" "$REPO/episodes/2026/january/$iso_date/article.md"
            echo "  ✓ Added local-intelligence: $iso_date"
        fi
    fi
done

# 3. Generate schema-enhanced index.html for each episode
echo "🎯 Step 3: Generating RadioEpisode schema pages..."

cat > /tmp/generate_schemas.py << 'SCHEMA_SCRIPT'
#!/usr/bin/env python3
import os
import re
import json
from datetime import datetime
from pathlib import Path

episodes_base = Path('/Users/macmini/sunshinefm-website/episodes/2026/january')

CV_LOCATIONS = {
    'Palm Springs', 'Rancho Mirage', 'Cathedral City', 'Indian Wells', 
    'La Quinta', 'Palm Desert', 'Desert Hot Springs', 'Indio', 'Coachella',
    'El Paseo', 'Coachella Valley', 'CV', 'Coachella'
}

def extract_entities(text):
    entities = {'people': [], 'organizations': [], 'places': []}
    
    # Extract locations
    for location in CV_LOCATIONS:
        if location.lower() in text.lower():
            if location not in entities['places']:
                entities['places'].append(location)
    
    # Extract named entities
    name_pattern = r'\b([A-Z][a-z]+ (?:[A-Z][a-z]+ )*[A-Z][a-z]+)\b'
    names = re.findall(name_pattern, text)
    
    for name in names:
        if name not in ['The', 'This', 'That', 'From', 'According', 'SunshineFM']:
            context = text[max(0, text.find(name)-100):text.find(name)+100].lower()
            if any(role in context for role in ['ceo', 'founder', 'developer', 'operator', 'executive']):
                if name not in entities['people']:
                    entities['people'].append(name)
            elif name not in entities['organizations']:
                entities['organizations'].append(name)
    
    return entities

# Process all episode folders
episodes = []
for date_folder in sorted(episodes_base.iterdir()):
    if not date_folder.is_dir():
        continue
    
    iso_date = date_folder.name
    article_path = date_folder / 'article.md'
    
    if not article_path.exists():
        continue
    
    with open(article_path, 'r') as f:
        article_content = f.read()
    
    entities = extract_entities(article_content)
    
    # Parse date
    try:
        date_obj = datetime.strptime(iso_date, '%Y-%m-%d')
        date_display = date_obj.strftime('%A, %B %d, %Y')
    except:
        date_display = iso_date
    
    # Build schema
    schema = {
        "@context": "https://schema.org/",
        "@type": "RadioEpisode",
        "url": f"https://research.sunshine.fm/episodes/2026/january/{iso_date}/",
        "name": f"SunshineFM Daily — {date_display}",
        "description": "Original reporting on AI, startups, and business in the Coachella Valley",
        "datePublished": f"{iso_date}T11:11:00-08:00",
        "author": {
            "@type": "Person",
            "name": "Sat Singh",
            "url": "https://sunshine.fm"
        },
        "broadcaster": {
            "@type": "RadioStation",
            "name": "SunshineFM",
            "url": "https://radio.co/sunshinefm"
        },
        "partOfSeries": {
            "@type": "RadioSeries",
            "name": "SunshineFM Daily",
            "url": "https://research.sunshine.fm/"
        },
        "areaServed": {
            "@type": "Place",
            "name": "Coachella Valley, California",
            "geo": {
                "@type": "GeoShape",
                "addressRegion": "CA"
            }
        },
        "mentions": []
    }
    
    # Add entities
    for place in ep['entities']['places'][:5]:
        schema['mentions'].append({"@type": "Place", "name": place})
    for person in ep['entities']['people'][:5]:
        schema['mentions'].append({"@type": "Person", "name": person})
    for org in ep['entities']['organizations'][:5]:
        schema['mentions'].append({"@type": "Organization", "name": org})
    
    # Generate HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SunshineFM Daily — {date_display}</title>
    <meta name="description" content="Original reporting from SunshineFM on {date_display}">
    <meta property="og:type" content="article">
    <meta property="og:title" content="SunshineFM Daily — {date_display}">
    <meta property="og:url" content="https://research.sunshine.fm/episodes/2026/january/{iso_date}/">
    
    <!-- RadioEpisode Schema with Coachella Valley Entities -->
    <script type="application/ld+json">
{json.dumps(schema, indent=2)}
    </script>
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.8; max-width: 750px; margin: 0 auto; padding: 40px 20px; color: #111418; background: #F7F7F2; }}
        h1 {{ font-size: 2.5em; color: #0B1F33; margin-bottom: 10px; font-weight: 700; }}
        .meta {{ background: #fff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #FFD84D; }}
        .meta p {{ margin: 5px 0; font-size: 0.95em; color: #666; }}
        .content {{ background: #fff; padding: 30px; border-radius: 8px; margin: 20px 0; }}
        .content p {{ margin-bottom: 18px; }}
        .entities {{ background: #f0f4ff; padding: 15px; border-radius: 6px; margin: 20px 0; font-size: 0.9em; }}
        .entity-tag {{ display: inline-block; background: #E8F4FF; color: #0B1F33; padding: 4px 10px; margin: 3px 3px 3px 0; border-radius: 4px; font-size: 0.85em; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #999; font-size: 0.9em; }}
        a {{ color: #4DA3FF; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>

<h1>SunshineFM Daily</h1>
<h2 style="font-size: 1.4em; color: #666; font-weight: 400; margin-bottom: 30px;">{date_display}</h2>

<div class="meta">
    <p><strong>📻 Broadcast:</strong> {date_display} at 11:11 AM PST</p>
    <p><strong>🎙️ Host:</strong> Sat Singh</p>
    <p><a href="https://github.com/SunshineFM/sunshinefm-website/tree/main/episodes/2026/january/{iso_date}" target="_blank">→ View on GitHub</a></p>
</div>

<div class="content">
{article_content}
</div>

{'<div class="entities"><h4>📍 Locations & Entities Mentioned</h4>' + ''.join([f'<span class="entity-tag">📍 {p}</span>' for p in entities['places']]) + ''.join([f'<span class="entity-tag">👤 {p}</span>' for p in entities['people'][:3]]) + ''.join([f'<span class="entity-tag">🏢 {o}</span>' for o in entities['organizations'][:3]]) + '</div>' if entities['places'] or entities['people'] or entities['organizations'] else ''}

<div class="footer">
    <p>SunshineFM Daily — Original reporting from the Coachella Valley</p>
    <p><a href="https://research.sunshine.fm/">← Episode Archive</a> | <a href="https://sunshine.fm">Main Site</a></p>
</div>

</body>
</html>'''
    
    # Write file
    index_path = date_folder / 'index.html'
    with open(index_path, 'w') as f:
        f.write(html)
    
    print(f"✅ {iso_date}: {', '.join(entities['places'][:2])} | {len(entities['people'])} people | {len(entities['organizations'])} orgs")

SCHEMA_SCRIPT

python3 /tmp/generate_schemas.py

# 4. Generate updated sitemap.xml
echo "🗺️  Step 4: Generating sitemap.xml with ISO date URLs..."

cat > "$REPO/sitemap.xml" << 'SITEMAP'
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
SITEMAP

# Add all episode URLs to sitemap
for episode_folder in "$REPO/episodes/2026/january"/*/; do
    iso_date=$(basename "$episode_folder")
    echo "  <url>" >> "$REPO/sitemap.xml"
    echo "    <loc>https://research.sunshine.fm/episodes/2026/january/$iso_date/</loc>" >> "$REPO/sitemap.xml"
    echo "    <lastmod>${iso_date}T11:11:00-08:00</lastmod>" >> "$REPO/sitemap.xml"
    echo "    <changefreq>daily</changefreq>" >> "$REPO/sitemap.xml"
    echo "    <priority>1.0</priority>" >> "$REPO/sitemap.xml"
    echo "  </url>" >> "$REPO/sitemap.xml"
done

# Add archive and homepage
cat >> "$REPO/sitemap.xml" << 'SITEMAP'
  <url>
    <loc>https://research.sunshine.fm/</loc>
    <lastmod>2026-01-24T00:00:00-08:00</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>
SITEMAP

# 5. Commit and prepare push
echo "💾 Step 5: Preparing Git commit..."
git add episodes/2026/
git add sitemap.xml
git status

echo ""
echo "✅ Steps 1-5 Complete!"
echo ""
echo "Step 6: Ready to commit and push"
echo ""
echo "Run these commands:"
echo "  git commit -m 'Reorganize episodes to clean ISO date structure (2026-01-XX)"
echo "  git push origin main"

