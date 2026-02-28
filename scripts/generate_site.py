#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
静态网站生成脚本
将新闻数据生成为静态 HTML 页面，输出到 docs/TechNews/
"""

import json
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

CST = timezone(timedelta(hours=8))

# 网站子路径前缀
BASE_PATH = "/TechNews"


def load_news(data_dir: Path, date_str: str = None) -> dict:
    if date_str:
        f = data_dir / f"{date_str}.json"
    else:
        f = data_dir / "latest.json"
    if not f.exists():
        return {}
    with open(f, "r", encoding="utf-8") as fp:
        return json.load(fp)


def load_index(data_dir: Path) -> list:
    f = data_dir / "index.json"
    if not f.exists():
        return []
    with open(f, "r", encoding="utf-8") as fp:
        return json.load(fp).get("dates", [])


def group_by_category(articles: list) -> dict:
    groups = {}
    for a in articles:
        cat = a.get("category", "其他")
        groups.setdefault(cat, []).append(a)
    return groups


def render_article_card(a: dict) -> str:
    title = a.get("title", "").replace("<", "&lt;").replace(">", "&gt;")
    url = a.get("url", "#")
    summary = a.get("summary", "").replace("<", "&lt;").replace(">", "&gt;")
    source = a.get("source", "")
    icon = a.get("icon", "📰")
    summary_html = f'<p class="summary">{summary}</p>' if summary else ""
    return f"""
    <article class="card">
      <h3><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>
      {summary_html}
      <footer><span class="source-badge">{icon} {source}</span></footer>
    </article>"""


def render_category_section(category: str, articles: list) -> str:
    cards = "".join(render_article_card(a) for a in articles)
    return f"""
  <section class="category-section">
    <h2 class="category-title">{category} <span class="count">({len(articles)})</span></h2>
    <div class="cards-grid">{cards}
    </div>
  </section>"""


def render_date_nav(dates: list, current: str) -> str:
    items = []
    for d in dates[:10]:
        active = ' class="active"' if d == current else ""
        items.append(f'<a href="{BASE_PATH}/{d}.html"{active}>{d}</a>')
    return "\n    ".join(items)


def render_page(data: dict, dates: list, out_path: Path):
    date_str = data.get("date", "")
    generated_at = data.get("generated_at", "")
    articles = data.get("articles", [])
    groups = group_by_category(articles)

    sections = "".join(
        render_category_section(cat, arts)
        for cat, arts in groups.items()
    )
    nav_html = render_date_nav(dates, date_str)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>科技日报 · {date_str}</title>
  <link rel="stylesheet" href="{BASE_PATH}/assets/style.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📡</text></svg>">
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <div class="logo">📡 科技日报</div>
      <p class="tagline">每日科技圈精选资讯 · 北京时间早 8 点更新</p>
    </div>
  </header>

  <nav class="date-nav">
    <div class="nav-inner">
      <span class="nav-label">历史存档：</span>
      {nav_html}
    </div>
  </nav>

  <main class="main-content">
    <div class="page-meta">
      <h1 class="page-date">📅 {date_str}</h1>
      <p class="meta-info">共收录 <strong>{len(articles)}</strong> 条资讯 · 更新于 {generated_at[:19].replace("T", " ")} CST</p>
    </div>
    {sections}
  </main>

  <footer class="site-footer">
    <p>数据来源：Hacker News · The Verge · TechCrunch · Wired · MIT TR · Ars Technica · 36氪 · 少数派</p>
    <p>由 <a href="https://github.com/features/actions" target="_blank">GitHub Actions</a> 自动生成 · 托管于 <a href="https://pages.github.com" target="_blank">GitHub Pages</a></p>
  </footer>

  <script src="{BASE_PATH}/assets/app.js"></script>
</body>
</html>"""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)


def generate_index_redirect(dates: list, docs_dir: Path):
    latest = dates[0] if dates else ""
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>科技日报</title>
  <script>location.replace("{BASE_PATH}/{latest}.html");</script>
</head>
<body></body>
</html>"""
    with open(docs_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html)


def copy_assets(docs_dir: Path):
    assets_src = Path("assets")
    assets_dst = docs_dir / "assets"
    if assets_src.exists():
        shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)


def main():
    data_dir = Path("data/news")
    # 输出到 docs/TechNews/，对应 143709123.xyz/TechNews/ 路径
    docs_dir = Path("docs/TechNews")
    docs_dir.mkdir(parents=True, exist_ok=True)

    dates = load_index(data_dir)
    print(f"📋 发现 {len(dates)} 天的存档")

    for date_str in dates:
        data = load_news(data_dir, date_str)
        if not data:
            continue
        out_path = docs_dir / f"{date_str}.html"
        render_page(data, dates, out_path)
        print(f"  ✅ 生成 {out_path}")

    if dates:
        # 只在 docs/TechNews/ 下生成 index.html，不覆盖根 docs/index.html
        generate_index_redirect(dates, docs_dir)
        print(f"  ✅ 生成 TechNews/index.html → {dates[0]}.html")

    copy_assets(docs_dir)
    print("🎉 网站生成完成")


if __name__ == "__main__":
    main()
