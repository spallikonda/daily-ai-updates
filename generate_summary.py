import os
import feedparser
import requests
from datetime import datetime
import markdown2
from weasyprint import HTML
from bs4 import BeautifulSoup

# === CONFIG ===
COMPANIES = {
    "OpenAI": "https://openai.com/news/rss.xml",
    "Anthropic": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",  # Community-generated
    "Google DeepMind": "https://deepmind.google/blog/feed.xml",  # Check if active; fallback to Google News
    "Microsoft AI": "https://news.microsoft.com/source/topics/ai/feed/",
    "xAI Grok": "https://x.ai/news/feed",  # If available, else manual
    "DeepSeek": "https://www.deepseek.com/news/rss",  # Add actual if found
    "Alibaba Qwen": "https://qwenlm.github.io/blog/feed.xml",
    "Meta Llama": "https://ai.meta.com/blog/feed/",  # Or RSSHub
    # Add more as needed
}

# Use Grok API (or switch to OpenAI/Anthropic)
from grokapi import Grok  # pip install grokapi or use openai library with xAI endpoint

client = Grok(api_key=os.getenv("GROK_API_KEY"))

def get_latest_news(company, url):
    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            return None
        entry = feed.entries[0]
        # Fetch full content if needed
        summary_prompt = f"""
        Summarize the latest update from {company} in **1-2 lines** only. 
        Focus on key facts, model/release name, impact. Include the link.
        Title: {entry.title}
        Description: {entry.description[:800]}
        Link: {entry.link}
        """
        response = client.chat.completions.create(
            model="grok-3",  # or latest
            messages=[{"role": "user", "content": summary_prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"**{company}**: No major updates today or error fetching feed."

# Generate content
today = datetime.now().strftime("%Y-%m-%d")
md_content = f"# Daily AI Updates from Top Companies\n**Date:** {today}\n\n"

for company, url in COMPANIES.items():
    summary = get_latest_news(company, url)
    if summary:
        md_content += f"{summary}\n\n"

md_content += "\n---\nGenerated automatically via GitHub Actions. [View all archives](https://github.com/YOURUSERNAME/daily-ai-updates/tree/main/summaries)"

# Save Markdown
os.makedirs("summaries", exist_ok=True)
with open(f"summaries/{today}.md", "w", encoding="utf-8") as f:
    f.write(md_content)

# Generate PDF
os.makedirs("pdfs", exist_ok=True)
html = markdown2.markdown(md_content, extras=["tables"])
HTML(string=html).write_pdf(f"pdfs/{today}.pdf")

print(f"✅ Generated summary for {today}")
