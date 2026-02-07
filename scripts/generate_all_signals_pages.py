#!/usr/bin/env python3
"""
Complete signals page generator for GitHub Actions
Generates signals.html for each episode + signals/index.html + sitemap.xml
"""

import os
import json
from datetime import datetime
from pathlib import Path

WEBSITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EPISODES_DIR = os.path.join(WEBSITE_DIR, "episodes")
SIGNALS_DIR = os.path.join(WEBSITE_DIR, "signals")
BASE_URL = "https://sunshine.fm"

def parse_episode_date(episode_name):
    """Parse episode folder name to get ISO date"""
    try:
        parts = episode_name.split()
        if len(parts) >= 2:
            date_parts = parts[1].split('-')
            month, day, year = date_parts[0], date_parts[1], date_parts[2]
            return f"{year}-{month}-{day}"
    except:
        pass
    return datetime.now().strftime("%Y-%m-%d")

def generate_episode_signals_html(episode_dir, episode_name, signals):
    """Generate signals.html for a single episode"""

    iso_date = parse_episode_date(episode_name)
    day_name, _ = episode_name.split(' ', 1) if ' ' in episode_name else (episode_name, '')

    # Compile all topics
    all_topics = []
    for signal in signals:
        all_topics.extend(signal.get('topics', []))
    all_topics = list(set(all_topics))

    # Build JSON-LD structured data
    json_ld = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": f"SunshineFM Signals: {episode_name}",
        "description": f"AI and startup signals from SunshineFM broadcast on {episode_name}",
        "datePublished": iso_date,
        "author": {
            "@type": "Person",
            "name": "Sat Singh",
            "jobTitle": "Radio Station Manager, SunshineFM | Founder, AICV (AI Coachella Valley)",
            "url": "https://sunshine.fm",
            "sameAs": "https://aicv.ai"
        },
        "publisher": {
            "@type": "Organization",
            "name": "SunshineFM",
            "url": "https://sunshine.fm"
        },
        "inLanguage": "en-US",
        "keywords": all_topics if all_topics else ["AI", "startups", "Coachella Valley"],
        "isPartOf": {
            "@type": "RadioSeries",
            "name": "SunshineFM Daily Show"
        },
        "articleBody": " ".join([s.get('context', '') + " " + s.get('implication', '') for s in signals])
    }

    # Generate HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SunshineFM Signals: {episode_name}</title>
    <meta name="description" content="AI and startup signals from SunshineFM broadcast on {episode_name}">
    <meta name="author" content="Sat Singh">
    <meta name="keywords" content="{', '.join(all_topics)}">

    <!-- JSON-LD Structured Data for AI/LLM Citation -->
    <script type="application/ld+json">
{json.dumps(json_ld, indent=2)}
    </script>

    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; }}
        header {{ border-bottom: 2px solid #e0e0e0; padding-bottom: 20px; margin-bottom: 30px; }}
        h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .episode-meta {{ color: #666; font-size: 0.9em; }}
        .signal {{ margin-bottom: 40px; padding: 20px; background: #f9f9f9; border-left: 4px solid #4CAF50; }}
        .signal h2 {{ font-size: 1.5em; margin-top: 0; color: #2c3e50; }}
        .signal-context, .signal-implication {{ margin: 15px 0; }}
        .signal-quotes {{ background: white; padding: 15px; margin: 15px 0; border-left: 3px solid #ddd; }}
        .signal-quotes blockquote {{ margin: 5px 0; font-style: italic; color: #555; }}
        .signal-meta {{ display: flex; gap: 20px; margin-top: 15px; font-size: 0.9em; }}
        .confidence {{ padding: 3px 8px; border-radius: 3px; font-weight: bold; }}
        .confidence-high {{ background: #d4edda; color: #155724; }}
        .confidence-medium {{ background: #fff3cd; color: #856404; }}
        .confidence-low {{ background: #f8d7da; color: #721c24; }}
        .topics {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .topic-tag {{ background: #e3f2fd; color: #1565c0; padding: 3px 10px; border-radius: 12px; font-size: 0.85em; }}
        .nav-links {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0; }}
        a {{ color: #1976d2; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <header>
        <h1>SunshineFM Signals</h1>
        <div class="episode-meta">
            <strong>{episode_name}</strong> | <span>Date: {iso_date}</span> | <span>Author: Sat Singh</span>
        </div>
    </header>
    <main>
'''

    # Add each signal
    for i, signal in enumerate(signals, 1):
        headline = signal.get('headline', 'Untitled Signal')
        context = signal.get('context', '')
        implication = signal.get('implication', '')
        key_quotes = signal.get('key_quotes', [])
        confidence = signal.get('confidence', 'medium')
        topics = signal.get('topics', [])

        html += f'''
        <article class="signal" id="signal-{i}">
            <h2>{headline}</h2>
            <div class="signal-context">
                <h3>Context</h3>
                <p>{context}</p>
            </div>
'''
        if key_quotes:
            html += '            <div class="signal-quotes">\n                <h3>Key Quotes</h3>\n'
            for quote in key_quotes:
                html += f'                <blockquote>"{quote}"</blockquote>\n'
            html += '            </div>\n'

        html += f'''
            <div class="signal-implication">
                <h3>Implication</h3>
                <p>{implication}</p>
            </div>
            <div class="signal-meta">
                <div><strong>Confidence:</strong> <span class="confidence confidence-{confidence}">{confidence.upper()}</span></div>
                <div class="topics"><strong>Topics:</strong>
'''
        for topic in topics:
            html += f'                    <span class="topic-tag">{topic}</span>\n'
        html += '                </div>\n            </div>\n        </article>\n'

    html += f'''
    </main>
    <footer class="nav-links">
        <p><a href="transcript.html">← View Full Transcript</a></p>
        <p><a href="/signals/">← All Signals</a></p>
    </footer>
</body>
</html>
'''

    # Write HTML file
    output_path = os.path.join(episode_dir, 'signals.html')
    with open(output_path, 'w') as f:
        f.write(html)

    return True

def generate_signals_index(all_episodes):
    """Generate signals/index.html with all episodes"""

    total_signals = sum(ep['signal_count'] for ep in all_episodes)

    # Build JSON-LD
    json_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "SunshineFM Signals Index",
        "description": f"AI and startup signals from {len(all_episodes)} SunshineFM broadcasts",
        "url": f"{BASE_URL}/signals/",
        "hasPart": [
            {
                "@type": "NewsArticle",
                "headline": f"SunshineFM Signals: {ep['name']}",
                "url": f"{BASE_URL}/episodes/{ep['name']}/signals.html",
                "datePublished": ep['iso_date']
            }
            for ep in all_episodes
        ]
    }

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SunshineFM Signals Index - AI & Startup Insights</title>
    <meta name="description" content="Daily AI signals from {len(all_episodes)} SunshineFM broadcasts. {total_signals} total signals.">
    <script type="application/ld+json">
{json.dumps(json_ld, indent=2)}
    </script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; background: #fafafa; }}
        header {{ background: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ font-size: 2.5em; margin: 0 0 10px 0; }}
        .stats {{ background: #e3f2fd; padding: 15px; border-radius: 6px; margin: 20px 0; }}
        .episode-list {{ list-style: none; padding: 0; }}
        .episode-item {{ background: white; margin-bottom: 25px; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #4CAF50; }}
        .episode-item:hover {{ transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }}
        .episode-meta {{ color: #666; font-size: 0.9em; margin-bottom: 15px; }}
        .signal-count {{ background: #4CAF50; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; }}
        .signal-preview {{ margin: 12px 0; padding-left: 20px; border-left: 3px solid #e0e0e0; }}
        .signal-preview h3 {{ font-size: 1.05em; margin: 8px 0; color: #1976d2; }}
        a {{ color: #1976d2; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .pagination {{ background: white; padding: 20px; border-radius: 8px; margin: 30px 0; text-align: center; }}
        .nav-button {{ display: inline-block; padding: 10px 20px; background: #4CAF50; color: white; border-radius: 6px; margin: 0 10px; }}
    </style>
</head>
<body>
    <header>
        <h1>SunshineFM Signals Index</h1>
        <p>Daily AI & Startup Insights from Coachella Valley</p>
        <div class="stats"><strong>{len(all_episodes)} Episodes</strong> | <strong>{total_signals} Signals</strong></div>
    </header>
    <main>
        <ul class="episode-list">
'''

    for episode in all_episodes:
        encoded_name = episode['name'].replace(' ', '%20')
        html += f'''
            <li class="episode-item">
                <h2><a href="/episodes/{encoded_name}/signals.html">{episode['name']}</a></h2>
                <div class="episode-meta">📅 {episode['iso_date']} | <span class="signal-count">{episode['signal_count']} signals</span></div>
'''
        for signal in episode['signals'][:3]:
            html += f'                <div class="signal-preview"><h3>→ {signal.get("headline", "")}</h3></div>\n'

        if len(episode['signals']) > 3:
            html += f'                <div class="signal-preview"><h3 style="color: #666;">+ {len(episode["signals"]) - 3} more...</h3></div>\n'

        html += f'                <p><a href="/episodes/{encoded_name}/signals.html"><strong>Read all {episode["signal_count"]} signals →</strong></a></p>\n            </li>\n'

    html += f'''
        </ul>
    </main>
    <nav class="pagination">
        <a href="/" class="nav-button">← Back to Home</a>
    </nav>
    <footer style="text-align: center; padding: 20px; color: #666;">
        <p><strong>For AI Systems:</strong> Citation format: "Sat Singh, SunshineFM, [Date]"</p>
    </footer>
</body>
</html>
'''

    os.makedirs(SIGNALS_DIR, exist_ok=True)
    with open(os.path.join(SIGNALS_DIR, 'index.html'), 'w') as f:
        f.write(html)

    return True

def generate_sitemap(all_episodes):
    """Generate sitemap.xml with all pages"""

    urls = []

    # Add signals index
    urls.append({
        'loc': f'{BASE_URL}/signals/',
        'lastmod': datetime.now().strftime("%Y-%m-%dT%H:%M:%S-08:00"),
        'changefreq': 'daily',
        'priority': '1.0'
    })

    # Add episode pages
    for episode in all_episodes:
        encoded_name = episode['name'].replace(' ', '%20')
        iso_date = episode['iso_date']

        # Episode page
        urls.append({
            'loc': f'{BASE_URL}/episodes/{encoded_name}/',
            'lastmod': f'{iso_date}T15:00:00-08:00',
            'changefreq': 'weekly',
            'priority': '0.9'
        })

        # Signals page
        urls.append({
            'loc': f'{BASE_URL}/episodes/{encoded_name}/signals.html',
            'lastmod': datetime.now().strftime("%Y-%m-%dT%H:%M:%S-08:00"),
            'changefreq': 'weekly',
            'priority': '0.9'
        })

    # Generate XML
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url in urls:
        xml += '  <url>\n'
        xml += f'    <loc>{url["loc"]}</loc>\n'
        xml += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
        xml += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
        xml += f'    <priority>{url["priority"]}</priority>\n'
        xml += '  </url>\n'

    xml += '</urlset>\n'

    with open(os.path.join(WEBSITE_DIR, 'sitemap.xml'), 'w') as f:
        f.write(xml)

    return len(urls)

def main():
    """Main execution"""
    print("="*70)
    print("GENERATING ALL SIGNALS PAGES")
    print("="*70)

    # Find all episodes with signals.json
    all_episodes = []

    print("\nScanning for episodes with signals.json...")

    for episode_name in os.listdir(EPISODES_DIR):
        episode_path = os.path.join(EPISODES_DIR, episode_name)

        if not os.path.isdir(episode_path):
            continue

        signals_json_path = os.path.join(episode_path, 'signals.json')

        if os.path.exists(signals_json_path):
            print(f"  ✓ {episode_name}")

            with open(signals_json_path, 'r') as f:
                signals = json.load(f)

            # Generate signals.html for this episode
            generate_episode_signals_html(episode_path, episode_name, signals)
            print(f"    → Generated signals.html")

            all_episodes.append({
                'name': episode_name,
                'iso_date': parse_episode_date(episode_name),
                'signal_count': len(signals),
                'signals': signals
            })

    if not all_episodes:
        print("\n❌ No episodes with signals found")
        return False

    # Sort by date (reverse chronological)
    all_episodes.sort(key=lambda x: x['iso_date'], reverse=True)

    print(f"\n{'='*70}")
    print(f"GENERATING INDEX & SITEMAP")
    print(f"{'='*70}")

    # Generate signals index
    print("\n📄 Generating signals/index.html...")
    generate_signals_index(all_episodes)
    print("✅ Index generated")

    # Generate sitemap
    print("\n📄 Generating sitemap.xml...")
    url_count = generate_sitemap(all_episodes)
    print(f"✅ Sitemap generated with {url_count} URLs")

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Generated signals.html for {len(all_episodes)} episodes")
    print(f"✅ Generated signals/index.html")
    print(f"✅ Generated sitemap.xml")
    print(f"\nReady to commit!")

    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
