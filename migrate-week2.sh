#!/bin/bash

REPO="/Users/macmini/sunshinefm-website"
cd "$REPO"

echo "📦 Migrating Week 2 episodes to clean structure..."

# Migrate the 4 missing week 2 episodes
mkdir -p episodes/2026/january/2026-01-20
mkdir -p episodes/2026/january/2026-01-21
mkdir -p episodes/2026/january/2026-01-22
mkdir -p episodes/2026/january/2026-01-23

cp "episodes/Tuesday 01-20-2026/article.md" episodes/2026/january/2026-01-20/
cp "episodes/Tuesday 01-20-2026/transcript.md" episodes/2026/january/2026-01-20/ 2>/dev/null || true

cp "episodes/Wednesday 01-21-2026/article.md" episodes/2026/january/2026-01-21/
cp "episodes/Wednesday 01-21-2026/transcript.md" episodes/2026/january/2026-01-21/ 2>/dev/null || true

cp "episodes/Thursday 01-22-2026/article.md" episodes/2026/january/2026-01-22/
cp "episodes/Thursday 01-22-2026/transcript.md" episodes/2026/january/2026-01-22/ 2>/dev/null || true

cp "episodes/Friday 01-23-2026/article.md" episodes/2026/january/2026-01-23/
cp "episodes/Friday 01-23-2026/transcript.md" episodes/2026/january/2026-01-23/ 2>/dev/null || true

echo "✅ Week 2 migrated"
echo ""
echo "Now regenerating all 11 episode schemas..."

python3 << 'PYTHON'
import os
import re
import json
from datetime import datetime
from pathlib import Path

episodes_base = Path('/Users/macmini/sunshinefm-website/episodes/2026/january')

CV_LOCATIONS = {
    'Palm Springs', 'Rancho Mirage', 'Cathedral City', 'Indian Wells', 
    'La Quinta', 'Palm Desert', 'Desert Hot Springs', 'Indio', 'Coachella',
    'El Paseo', 'Coachella Valley', 'CV'
}

def extract_entities(text):
    entities = {'people': [], 'organizations': [], 'places': []}
    
    for location in CV_LOCATIONS:
        if location.lower() in text.lower():
            if location not in entities['places']:
                entities['places'].append(location)
    
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

count = 0
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
    
    try:
        date_obj = datetime.strptime(iso_date, '%Y-%m-%d')
        date_display = date_obj.strftime('%A, %B %d, %Y')
    except:
        date_display = iso_date
    
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
    
    for place in entities['places'][:5]:
        schema['mentions'].append({"@type": "Place", "name": place})
    for person in entities['people'][:5]:
        schema['mentions'].append({"@type": "Person", "name": person})
    for org in entities['organizations'][:5]:
        schema['mentions'].append({"@type": "Organization", "name": org})
    
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
    
    index_path = date_folder / 'index.html'
    with open(index_path, 'w') as f:
        f.write(html)
    
    places = ', '.join(entities['places'][:2]) if entities['places'] else 'N/A'
    print(f"✅ {iso_date}: {places}")
    count += 1

print(f"\n✨ Generated {count}/11 episode pages")

PYTHON

