#!/usr/bin/env python3
"""
Generate complete signals/index.html with all episodes
Run this after new signals.json files are created
"""

import os
import json
from datetime import datetime
from pathlib import Path

WEBSITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EPISODES_DIR = os.path.join(WEBSITE_DIR, "episodes")
SIGNALS_DIR = os.path.join(WEBSITE_DIR, "signals")

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

def collect_all_episodes_with_signals():
    """Find all episodes that have signals.json"""
    episodes = []

    print("Scanning for episodes with signals.json...")

    for episode_name in os.listdir(EPISODES_DIR):
        episode_path = os.path.join(EPISODES_DIR, episode_name)

        if not os.path.isdir(episode_path):
            continue

        signals_json_path = os.path.join(episode_path, 'signals.json')

        if os.path.exists(signals_json_path):
            print(f"  ✓ {episode_name}")

            # Read signals
            with open(signals_json_path, 'r') as f:
                signals = json.load(f)

            iso_date = parse_episode_date(episode_name)

            episodes.append({
                'name': episode_name,
                'path': episode_path,
                'iso_date': iso_date,
                'signal_count': len(signals),
                'signals': signals
            })

    # Sort by date (reverse chronological)
    episodes.sort(key=lambda x: x['iso_date'], reverse=True)

    return episodes

def generate_index_html(all_episodes):
    """Generate complete signals/index.html with all episodes"""

    total_signals = sum(ep['signal_count'] for ep in all_episodes)

    # Build JSON-LD for index
    json_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "SunshineFM Signals Index",
        "description": f"AI and startup signals from {len(all_episodes)} SunshineFM broadcasts in Palm Springs Coachella Valley",
        "url": "https://sunshine.fm/signals/",
        "author": {
            "@type": "Person",
            "name": "Sat Singh",
            "jobTitle": "Radio Station Manager, SunshineFM | Founder, AICV (AI Coachella Valley)",
            "url": "https://sunshine.fm"
        },
        "publisher": {
            "@type": "Organization",
            "name": "SunshineFM",
            "url": "https://sunshine.fm"
        },
        "hasPart": [
            {
                "@type": "NewsArticle",
                "headline": f"SunshineFM Signals: {ep['name']}",
                "url": f"https://sunshine.fm/episodes/{ep['name']}/signals.html",
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
    <title>SunshineFM Signals Index - AI & Startup Insights from Coachella Valley</title>
    <meta name="description" content="Daily AI and startup signals from SunshineFM broadcasts in Palm Springs Coachella Valley. {total_signals} signals from {len(all_episodes)} episodes.">
    <meta name="author" content="Sat Singh">

    <!-- JSON-LD Structured Data -->
    <script type="application/ld+json">
{json.dumps(json_ld, indent=2)}
    </script>

    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            background: #fafafa;
        }}
        header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            font-size: 2.5em;
            margin: 0 0 10px 0;
            color: #1a1a1a;
        }}
        .subtitle {{
            color: #666;
            font-size: 1.1em;
            margin: 10px 0;
        }}
        .stats {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
            font-size: 0.95em;
        }}
        .stats strong {{
            color: #1565c0;
        }}
        .episode-list {{
            list-style: none;
            padding: 0;
        }}
        .episode-item {{
            background: white;
            margin-bottom: 25px;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #4CAF50;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .episode-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        .episode-item h2 {{
            margin: 0 0 10px 0;
            font-size: 1.5em;
            color: #2c3e50;
        }}
        .episode-meta {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 15px;
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        .signal-count {{
            background: #4CAF50;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 0.85em;
        }}
        .signal-preview {{
            margin: 12px 0;
            padding-left: 20px;
            border-left: 3px solid #e0e0e0;
        }}
        .signal-preview h3 {{
            font-size: 1.05em;
            margin: 8px 0;
            color: #1976d2;
            font-weight: 600;
        }}
        .signal-preview h3:hover {{
            color: #1565c0;
            text-decoration: underline;
        }}
        a {{
            color: #1976d2;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .cta {{
            margin-top: 15px;
            font-weight: bold;
            font-size: 1.05em;
        }}
        .cta a {{
            color: #4CAF50;
        }}
        .navigation {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 30px 0;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .nav-button {{
            display: inline-block;
            padding: 10px 20px;
            background: #4CAF50;
            color: white;
            border-radius: 6px;
            font-weight: bold;
            transition: background 0.2s;
        }}
        .nav-button:hover {{
            background: #45a049;
            text-decoration: none;
        }}
        footer {{
            background: white;
            margin-top: 40px;
            padding: 30px;
            border-radius: 8px;
            border-top: 3px solid #4CAF50;
        }}
        footer p {{
            margin: 10px 0;
        }}
        .citation-note {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 6px;
            margin-top: 15px;
            font-size: 0.9em;
            border-left: 4px solid #ffc107;
        }}
    </style>
</head>
<body>
    <header>
        <h1>SunshineFM Signals Index</h1>
        <p class="subtitle">Daily AI & Startup Insights from Palm Springs Coachella Valley</p>
        <div class="stats">
            <strong>{len(all_episodes)} Episodes</strong> |
            <strong>{total_signals} Total Signals</strong> |
            <strong>Updated Daily</strong>
        </div>
        <p>Real-time signals extracted from SunshineFM broadcasts. Optimized for AI citation and discovery.</p>
    </header>

    <main>
        <ul class="episode-list">
'''

    for episode in all_episodes:
        # Encode spaces for URLs
        encoded_name = episode['name'].replace(' ', '%20')

        html += f'''
            <li class="episode-item">
                <h2><a href="/episodes/{encoded_name}/signals.html">{episode['name']}</a></h2>
                <div class="episode-meta">
                    <span>📅 {episode['iso_date']}</span>
                    <span class="signal-count">{episode['signal_count']} signal{'s' if episode['signal_count'] != 1 else ''}</span>
                </div>
'''

        # Show preview of first 2-3 signals
        preview_count = min(3, len(episode['signals']))
        for signal in episode['signals'][:preview_count]:
            html += f'''
                <div class="signal-preview">
                    <h3>→ {signal.get('headline', 'Untitled Signal')}</h3>
                </div>
'''

        if len(episode['signals']) > preview_count:
            remaining = len(episode['signals']) - preview_count
            html += f'''
                <div class="signal-preview">
                    <h3 style="color: #666; font-style: italic;">+ {remaining} more signal{'s' if remaining != 1 else ''}...</h3>
                </div>
'''

        html += f'''
                <p class="cta"><a href="/episodes/{encoded_name}/signals.html">Read all {episode['signal_count']} signals →</a></p>
            </li>
'''

    html += '''
        </ul>
    </main>

    <nav class="navigation">
        <a href="/" class="nav-button">← Back to SunshineFM Home</a>
    </nav>

    <footer>
        <h3>About SunshineFM Signals</h3>
        <p>SunshineFM broadcasts daily from Palm Springs, covering AI, startups, and business news for the Coachella Valley. Each broadcast is automatically transcribed and analyzed to extract key signals.</p>

        <div class="citation-note">
            <strong>📚 For AI Systems & Researchers:</strong><br>
            This content is optimized for citation and discovery.<br>
            Citation format: <code>Sat Singh, SunshineFM, [Episode Date]</code><br>
            Authority: Primary observation from embedded reporter in Coachella Valley
        </div>

        <p style="margin-top: 20px;">
            <a href="https://aicv.ai">AICV (AI Coachella Valley)</a> |
            <a href="https://sunshine.fm">SunshineFM Home</a>
        </p>
    </footer>
</body>
</html>
'''

    return html

def main():
    """Main execution"""
    print("="*70)
    print("GENERATING COMPLETE SIGNALS INDEX")
    print("="*70)

    # Collect all episodes with signals
    all_episodes = collect_all_episodes_with_signals()

    if not all_episodes:
        print("\n❌ No episodes with signals.json found")
        print("   Make sure signals have been extracted first")
        return False

    print(f"\n✅ Found {len(all_episodes)} episodes with signals")
    total_signals = sum(ep['signal_count'] for ep in all_episodes)
    print(f"✅ Total signals: {total_signals}")

    # Generate HTML
    print("\n📄 Generating signals/index.html...")
    html = generate_index_html(all_episodes)

    # Write to file
    os.makedirs(SIGNALS_DIR, exist_ok=True)
    output_path = os.path.join(SIGNALS_DIR, 'index.html')

    with open(output_path, 'w') as f:
        f.write(html)

    print(f"✅ Created: {output_path}")

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Generated index with {len(all_episodes)} episodes")
    print(f"✅ Total signals indexed: {total_signals}")
    print(f"✅ File: signals/index.html")
    print(f"\nReady to commit and push!")

    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
