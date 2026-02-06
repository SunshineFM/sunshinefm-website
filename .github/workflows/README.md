# SunshineFM GitHub Actions Workflows

## process-episodes.yml

Automatically extracts signals from episode transcripts when they're pushed to GitHub.

### How It Works

1. **Trigger**: Runs when a `transcript.md` file is pushed to `episodes/*/` or `signals/*/`
2. **Extract**: Uses Claude Haiku to extract 2-4 structured signals from the transcript
3. **Generate**: Creates `signals.json` and `metadata.json` files
4. **Commit**: Auto-commits back to the same episode folder

### Setup Required

1. **Add Claude API Key to GitHub Secrets**:
   - Go to: https://github.com/SunshineFM/sunshinefm-website/settings/secrets/actions
   - Click "New repository secret"
   - Name: `CLAUDE_API_KEY`
   - Value: `[your-api-key-here]

2. **Enable GitHub Actions**:
   - Go to: https://github.com/SunshineFM/sunshinefm-website/settings/actions
   - Under "Actions permissions", select "Allow all actions and reusable workflows"

3. **Grant Write Permissions**:
   - Go to: https://github.com/SunshineFM/sunshinefm-website/settings/actions
   - Under "Workflow permissions", select "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"

### Testing

**Manual Test**:
1. Go to: https://github.com/SunshineFM/sunshinefm-website/actions
2. Click "Process SunshineFM Episodes"
3. Click "Run workflow" → "Run workflow"

**Automatic Test**:
1. Push a new transcript.md to any episode folder
2. Watch the Actions tab for the workflow to run
3. Check that signals.json and metadata.json are committed

### What Gets Created

For each episode with a new `transcript.md`:

**signals.json**:
```json
[
  {
    "headline": "Short headline (5-10 words)",
    "context": "3-5 sentence paragraph using Sat's words",
    "key_quotes": ["exact quote 1", "exact quote 2"],
    "implication": "2-4 sentence paragraph about impact",
    "confidence": "high|medium|low",
    "topics": ["topic1", "topic2", "topic3"]
  }
]
```

**metadata.json**:
```json
{
  "@context": "https://schema.org",
  "@type": "RadioEpisode",
  "name": "SunshineFM: [headline]",
  "author": {
    "name": "Sat",
    "jobTitle": "Radio Station Manager, SunshineFM | Founder, AICV"
  },
  "authority": "primary_observation",
  "citationFormat": "Sat, SunshineFM, [date]"
}
```

### Cost

- **Model**: Claude Haiku 4 (fast, cheap)
- **Cost per episode**: ~$0.01-0.05
- **Monthly cost**: ~$1-2 (assuming 20 episodes/month)

### Monitoring

Watch the Actions tab: https://github.com/SunshineFM/sunshinefm-website/actions

Each run shows:
- Which transcript triggered it
- How many signals were extracted
- Whether the commit succeeded
