#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科技圈每日新闻抓取脚本
从多个科技新闻源抓取最新资讯
"""

import json
import os
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup

# 北京时间 UTC+8
CST = timezone(timedelta(hours=8))

# 新闻源配置
NEWS_SOURCES = [
    {
        "name": "Hacker News",
        "url": "https://news.ycombinator.com/rss",
        "type": "rss",
        "category": "综合科技",
        "icon": "🔶"
    },
    {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "type": "rss",
        "category": "科技资讯",
        "icon": "📱"
    },
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/feed/",
        "type": "rss",
        "category": "创业科技",
        "icon": "🚀"
    },
    {
        "name": "Wired",
        "url": "https://www.wired.com/feed/rss",
        "type": "rss",
        "category": "科技文化",
        "icon": "⚡"
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
        "type": "rss",
        "category": "前沿技术",
        "icon": "🔬"
    },
    {
        "name": "Ars Technica",
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "type": "rss",
        "category": "深度科技",
        "icon": "🖥️"
    },
    {
        "name": "36氪",
        "url": "https://36kr.com/feed",
        "type": "rss",
        "category": "国内科技",
        "icon": "🇨🇳"
    },
    {
        "name": "少数派",
        "url": "https://sspai.com/feed",
        "type": "rss",
        "category": "数字生活",
        "icon": "📲"
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def clean_html(text: str) -> str:
    """清理 HTML 标签"""
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ", strip=True)[:300]


def fetch_rss(source: dict) -> list:
    """抓取 RSS 源"""
    articles = []
    try:
        feed = feedparser.parse(source["url"])
        for entry in feed.entries[:8]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = clean_html(
                entry.get("summary", entry.get("description", ""))
            )
            published = entry.get("published", entry.get("updated", ""))

            if title and link:
                articles.append({
                    "title": title,
                    "url": link,
                    "summary": summary,
                    "source": source["name"],
                    "category": source["category"],
                    "icon": source["icon"],
                    "published": published,
                })
    except Exception as e:
        print(f"[WARN] 抓取 {source['name']} 失败: {e}")
    return articles


def fetch_all_news() -> list:
    """抓取所有新闻源"""
    all_articles = []
    for source in NEWS_SOURCES:
        print(f"  → 抓取 {source['name']} ...")
        articles = fetch_rss(source)
        all_articles.extend(articles)
        time.sleep(1)
    return all_articles


def save_news(articles: list, output_dir: Path):
    """保存新闻数据"""
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(CST)
    date_str = now.strftime("%Y-%m-%d")

    data = {
        "date": date_str,
        "generated_at": now.isoformat(),
        "total": len(articles),
        "articles": articles,
    }

    # 保存当日数据
    daily_file = output_dir / f"{date_str}.json"
    with open(daily_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 更新 latest.json
    latest_file = output_dir / "latest.json"
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 更新索引
    update_index(output_dir, date_str)

    print(f"✅ 已保存 {len(articles)} 条新闻到 {daily_file}")
    return date_str


def update_index(output_dir: Path, new_date: str):
    """更新日期索引文件"""
    index_file = output_dir / "index.json"
    dates = []

    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            dates = json.load(f).get("dates", [])

    if new_date not in dates:
        dates.insert(0, new_date)
        dates = dates[:30]  # 保留最近30天

    with open(index_file, "w", encoding="utf-8") as f:
        json.dump({"dates": dates}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("🚀 开始抓取科技新闻...")
    data_dir = Path("data/news")
    articles = fetch_all_news()
    date_str = save_news(articles, data_dir)
    print(f"📅 {date_str} 新闻抓取完成，共 {len(articles)} 条")
