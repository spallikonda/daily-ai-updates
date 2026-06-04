import os
import feedparser
from datetime import datetime
import markdown2
from weasyprint import HTML
from openai import OpenAI

# === CONFIG ===
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

# xAI Grok Client (compatible with OpenAI library)
client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),      # ← Change secret name if you want
    base_url="https://api.x.ai/v1",
)

def get_latest_news(company, url):
    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            return f"**{company}**: No major updates in the last 24h."

        entry = feed.entries[0]
        prompt = f"""
        Create a crisp 1-2 line summary for a daily AI newsletter about this update from {company}.
        Be factual, neutral, and mention key points (model name, feature, impact).
        Title: {entry.title}
        Description: {entry.description[:700] if hasattr(entry, 'description') else ''}
        Link: {entry.link}
        """

        response = client.chat.completions.create(
            model="grok-4",           # or grok-3, grok-4.3 etc.
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        summary = response.choices[0].message.content.strip()
        return f"**{company}**: {summary}\nSource: [{entry.title}]({entry.link})"

    except Exception as e:
        print(f"Error fetching {company}: {e}")
        return f"**{company}**: No major updates today."

# === GENERATE SUMMARY ===
today = datetime.now().strftime("%Y-%m-%d")
md_content = f"# Daily AI Updates from Top Companies\n**Date:** {today}\n\n"

for company, url in COMPANIES.items():
    summary = get_latest_news(company, url)
    md_content += f"{summary}\n\n"

md_content += "\n---\nAuto-generated daily at 8 PM IST • Powered by GitHub Actions + Grok"

# Save files
os.makedirs("summaries", exist_ok=True)
os.makedirs("pdfs", exist_ok=True)

with open(f"summaries/{today}.md", "w", encoding="utf-8") as f:
    f.write(md_content)

# Generate PDF
html_content = markdown2.markdown(md_content, extras=["tables", "fenced-code-blocks"])
HTML(string=html_content).write_pdf(f"pdfs/{today}.pdf")

print(f"✅ Daily summary generated for {today}")
