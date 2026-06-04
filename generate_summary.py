import os
import feedparser
from datetime import datetime
import markdown2
from openai import OpenAI

# === COMPANIES & RSS ===
COMPANIES = {
    "OpenAI": "https://openai.com/news/rss.xml",
    "Anthropic": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
    "Google DeepMind": "https://deepmind.google/blog/rss.xml",
    "Microsoft AI": "https://news.microsoft.com/source/topics/ai/feed/",
    "xAI Grok": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_xainews.xml",
    "DeepSeek": "https://huggingface.co/blog/feed.xml",
    "Alibaba Qwen": "https://qwenlm.github.io/blog/feed.xml",
    "Meta Llama": "https://ai.meta.com/blog/feed/",
}

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

def get_latest_news(company, url):
    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            return f"**{company}**: No major updates today."

        entry = feed.entries[0]
        prompt = f"""
        Write a crisp 1-2 line summary for a daily AI newsletter.
        Company: {company}
        Title: {entry.title}
        Description: {getattr(entry, 'description', '')[:700]}
        Link: {entry.link}
        """

        response = client.chat.completions.create(
            model="grok-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0.6
        )
        summary = response.choices[0].message.content.strip()
        return f"**{company}**: {summary}\nSource: [{entry.title}]({entry.link})"
    except Exception as e:
        print(f"⚠️ Error with {company}: {e}")
        return f"**{company}**: No major updates today."

# Generate content
today = datetime.now().strftime("%Y-%m-%d")
md_content = f"# 🚀 Daily AI Updates\n**Date:** {today}\n\n"

for company, url in COMPANIES.items():
    summary = get_latest_news(company, url)
    md_content += summary + "\n\n"

md_content += "\n---\nAuto-generated at 8 PM IST • [GitHub Repo](https://github.com/YOUR-USERNAME/daily-ai-updates)"

# Save Markdown
os.makedirs("summaries", exist_ok=True)
os.makedirs("pdfs", exist_ok=True)

md_path = f"summaries/{today}.md"
pdf_path = f"pdfs/{today}.pdf"

with open(md_path, "w", encoding="utf-8") as f:
    f.write(md_content)

# Convert Markdown to PDF using md-to-pdf
import subprocess
subprocess.run(["md-to-pdf", md_path, "--output", pdf_path], check=True)

print(f"✅ Successfully generated summary + PDF for {today}")
