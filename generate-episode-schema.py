#!/usr/bin/env python3
import os
import re
from datetime import datetime
from pathlib import Path
import json

episodes_dir = Path('/Users/macmini/sunshinefm-website/episodes')

# Common Coachella Valley entities/patterns to look for
CV_LOCATIONS = {
    'Palm Springs', 'Rancho Mirage', 'Cathedral City', 'Indian Wells', 
    'La Quinta', 'Palm Desert', 'Desert Hot Springs', 'Indio', 'Coachella',
    'El Paseo', 'Coachella Valley', 'CV'
}

# Function to extract entities from article text
def extract_entities(text):
    entities = {'people': [], 'organizations': [], 'places': []}
    
    # Extract locations (CV places)
    for location in CV_LOCATIONS:
        if location.lower() in text.lower():
            if location not in entities['places']:
                entities['places'].append(location)
    
    # Extract capitalized phrases (potential people/orgs)
    # Pattern: Capitalized Name(s) [optional middle name] 
    name_pattern = r'\b([A-Z][a-z]+ (?:[A-Z][a-z]+ )*[A-Z][a-z]+)\b'
    names = re.findall(name_pattern, text)
    
    for name in names:
        # Filter out common words
        if name not in ['The', 'This', 'That', 'From', 'According']:
            # Simple heuristic: if mentions "developer", "CEO", etc., it's probably a person
            context = text[max(0, text.find(name)-100):text.find(name)+100].lower()
            if any(role in context for role in ['ceo', 'founder', 'developer', 'operator', 'executive', 'officer']):
                if name not in entities['people']:
                    entities['people'].append(name)
            # Otherwise could be org
            elif name not in entities['organizations']:
                entities['organizations'].append(name)
    
    return entities

# Collect and sort episodes
episodes = []
for folder in episodes_dir.iterdir():
    if not folder.is_dir() or folder.name.startswith('.'):
        continue
    
    article_path = folder / 'article.md'
    if not article_path.exists():
        continue
    
    try:
        folder_name = folder.name
        date_part = folder_name.split()[-1]
        day, month, year = date_part.split('-')
        iso_date = f"{year}-{month}-{day}"
        date_obj = datetime.strptime(iso_date, '%Y-%m-%d')
        
        with open(article_path, 'r') as f:
            article_content = f.read()
        
        entities = extract_entities(article_content)
        
        episodes.append({
            'folder': folder,
            'folder_name': folder_name,
            'iso_date': iso_date,
            'date_obj': date_obj,
            'article_content': article_content,
            'entities': entities
        })
    except Exception as e:
        print(f"⚠️  Skipped {folder.name}: {e}")

# Sort newest first
episodes.sort(key=lambda x: x['date_obj'], reverse=True)

print(f"Processing {len(episodes)} episodes...\n")

# Generate HTML for each episode
for ep in episodes:
    # Build schema with entities
    schema = {
        "@context": "https://schema.org/",
        "@type": "RadioEpisode",
        "url": f"https://research.sunshine.fm/episodes/{ep['folder_name'].replace(' ', '-')}/",
        "name": f"SunshineFM Daily — {ep['folder_name']}",
        "description": "Original reporting on AI, startups, and business in the Coachella Valley",
        "datePublished": f"{ep['iso_date']}T11:11:00-08:00",
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
    
    # Add extracted entities to mentions
    for place in ep['entities']['places']:
        schema['mentions'].append({
            "@type": "Place",
            "name": place
        })
    
    for person in ep['entities']['people'][:5]:  # Limit to 5
        schema['mentions'].append({
            "@type": "Person",
            "name": person
        })
    
    for org in ep['entities']['organizations'][:5]:  # Limit to 5
        schema['mentions'].append({
            "@type": "Organization",
            "name": org
        })
    
    # Generate HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SunshineFM Daily — {ep['folder_name']}</title>
    <meta name="description" content="SunshineFM original reporting from {ep['folder_name']}">
    <meta property="og:type" content="article">
    <meta property="og:title" content="SunshineFM Daily — {ep['folder_name']}">
    <meta property="og:url" content="https://research.sunshine.fm/episodes/{ep['folder_name'].replace(' ', '-')}//">
    
    <!-- RadioEpisode Schema with Local Entities -->
    <script type="application/ld+json">
{json.dumps(schema, indent=2)}
    </script>
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.8; max-width: 700px; margin: 0 auto; padding: 40px 20px; color: #111418; background: #F7F7F2; }}
        h1 {{ font-size: 2.5em; color: #0B1F33; margin-bottom: 10px; font-weight: 700; }}
        .meta {{ background: #fff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #FFD84D; }}
        .meta p {{ margin: 5px 0; font-size: 0.95em; color: #666; }}
        .content {{ background: #fff; padding: 30px; border-radius: 8px; margin: 20px 0; line-height: 1.8; }}
        .content p {{ margin-bottom: 20px; }}
        .content strong {{ color: #0B1F33; }}
        .entities {{ background: #f8f9fa; padding: 15px; border-radius: 6px; margin: 20px 0; font-size: 0.9em; }}
        .entities h4 {{ color: #4DA3FF; font-size: 0.9em; margin-bottom: 8px; }}
        .entity-tag {{ display: inline-block; background: #E8F4FF; color: #0B1F33; padding: 4px 8px; margin: 3px 3px 3px 0; border-radius: 4px; font-size: 0.85em; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #999; font-size: 0.9em; }}
        a {{ color: #4DA3FF; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>

<h1>SunshineFM Daily</h1>
<h2 style="font-size: 1.3em; color: #666; font-weight: 400; margin-bottom: 30px;">{ep['folder_name']}</h2>

<div class="meta">
    <p><strong>Original Radio Broadcast:</strong> {ep['folder_name']}</p>
    <p><strong>Published:</strong> {ep['iso_date']}</p>
    <p><strong>Host:</strong> Sat Singh</p>
    <p><a href="https://github.com/SunshineFM/sunshinefm-website/tree/main/episodes/{ep['folder_name'].replace(' ', '%20')}" target="_blank">→ View transcript on GitHub</a></p>
</div>

<div class="content">
{ep['article_content']}
</div>

{'<div class="entities"><h4>📍 Locations & Entities Mentioned</h4>' + ''.join([f'<span class="entity-tag">📍 {place}</span>' for place in ep['entities']['places']]) + ''.join([f'<span class="entity-tag">👤 {person}</span>' for person in ep['entities']['people'][:3]]) + ''.join([f'<span class="entity-tag">🏢 {org}</span>' for org in ep['entities']['organizations'][:3]]) + '</div>' if ep['entities']['places'] or ep['entities']['people'] or ep['entities']['organizations'] else ''}

<div class="footer">
    <p>SunshineFM Daily — Original reporting from the Coachella Valley</p>
    <p><a href="https://research.sunshine.fm/">← Back to archive</a> | <a href="https://sunshine.fm">Main site</a></p>
</div>

</body>
</html>'''
    
    # Write file
    index_path = ep['folder'] / 'index.html'
    with open(index_path, 'w') as f:
        f.write(html)
    
    entities_summary = f"{len(ep['entities']['places'])} places, {len(ep['entities']['people'])} people, {len(ep['entities']['organizations'])} orgs"
    print(f"✅ {ep['folder_name']:<25} → {entities_summary}")

print(f"\n✨ Generated {len(episodes)} episode pages with RadioEpisode schema")
