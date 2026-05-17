"""
collector.py — Nœud LangGraph : Agent de collecte
Auteur  : Hamza — Personne 1
Projet  : Cellule automatisée de veille technologique & stratégique
"""

import json, csv, time, logging, os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict, Annotated
import operator

import requests
from bs4 import BeautifulSoup
import feedparser
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
HF_TOKEN     = os.getenv("HF_TOKEN", "")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            LOGS_DIR / f"collector_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            encoding="utf-8"
        ),
        logging.StreamHandler(),
    ],
)

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

GITHUB_HEADERS = {
    **HEADERS,
    **({"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {})
}

HF_HEADERS = {
    **HEADERS,
    **({"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {})
}


class CollectorState(TypedDict):
    articles           : Annotated[list[dict], operator.add]
    repos              : Annotated[list[dict], operator.add]
    models             : Annotated[list[dict], operator.add]
    papers             : Annotated[list[dict], operator.add]
    hackernews_posts   : Annotated[list[dict], operator.add]
    collected_at       : str
    status             : str
    analysis_result    : dict
    knowledge_base     : dict
    report             : str


RSS_SOURCES = {
    "HuggingFace Blog"      : "https://huggingface.co/blog/feed.xml",
    "OpenAI Blog"           : "https://openai.com/blog/rss.xml",
    "Google DeepMind Blog"  : "https://deepmind.google/blog/rss.xml",
    "Meta AI Blog"          : "https://ai.meta.com/blog/feed/",
    "MIT Tech Review AI"    : "https://www.technologyreview.com/feed/",
    "ArXiv cs.AI"           : "https://export.arxiv.org/rss/cs.AI",
    "ArXiv cs.LG"           : "https://export.arxiv.org/rss/cs.LG",
    "Towards Data Science"  : "https://towardsdatascience.com/feed",
    "The Gradient"          : "https://thegradient.pub/rss/",
    "AI Alignment Forum"    : "https://www.alignmentforum.org/feed.xml",
}


def _collect_rss(source_name, url, max_items=8):
    items = []

    try:
        feed = feedparser.parse(url)

        if feed.bozo and not feed.entries:
            log.warning(f"[RSS] Flux invalide : {source_name}")
            return items

        for entry in feed.entries[:max_items]:
            items.append({
                "source": source_name,
                "type": "article",
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", ""),
                "summary": BeautifulSoup(
                    entry.get("summary", ""),
                    "html.parser"
                ).get_text(separator=" ", strip=True)[:400],
                "published": entry.get("published", entry.get("updated", "")),
                "collected_at": datetime.now(timezone.utc).isoformat(),
            })

        log.info(f"[RSS] {source_name} → {len(items)} articles")

    except Exception as e:
        log.error(f"[RSS] {source_name} : {e}")

    return items


def _collect_github_trending(language="python", since="daily"):
    items = []

    try:
        resp = requests.get(
            f"https://github.com/trending/{language}?since={since}",
            headers=GITHUB_HEADERS,
            timeout=15
        )

        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        for repo in soup.select("article.Box-row"):

            name_tag = repo.select_one("h2 a")

            if not name_tag:
                continue

            repo_path = name_tag["href"].strip("/")

            desc_tag  = repo.select_one("p")
            stars_tag = repo.select_one("a[href$='/stargazers']")
            today_tag = repo.select_one("span.d-inline-block.float-sm-right")
            lang_tag  = repo.select_one("[itemprop='programmingLanguage']")

            items.append({
                "source": "GitHub Trending",
                "type": "repo",
                "title": repo_path,
                "url": f"https://github.com/{repo_path}",
                "summary": desc_tag.get_text(strip=True) if desc_tag else "",
                "stars_total": stars_tag.get_text(strip=True) if stars_tag else "",
                "stars_today": today_tag.get_text(strip=True) if today_tag else "",
                "language": lang_tag.get_text(strip=True) if lang_tag else language,
                "collected_at": datetime.now(timezone.utc).isoformat(),
            })

        log.info(f"[GitHub] trending/{language} → {len(items)} repos")

    except Exception as e:
        log.error(f"[GitHub] {e}")

    return items


def _collect_hackernews(limit=15):
    items = []

    try:
        top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"

        story_ids = requests.get(top_url, timeout=15).json()[:limit]

        for sid in story_ids:

            item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"

            data = requests.get(item_url, timeout=15).json()

            if not data:
                continue

            items.append({
                "source": "Hacker News",
                "type": "tech_news",
                "title": data.get("title", ""),
                "url": data.get("url", ""),
                "summary": f"Score: {data.get('score',0)} | Comments: {data.get('descendants',0)}",
                "score": data.get("score", 0),
                "num_comments": data.get("descendants", 0),
                "published": datetime.fromtimestamp(
                    data.get("time", 0),
                    tz=timezone.utc
                ).isoformat(),
                "collected_at": datetime.now(timezone.utc).isoformat(),
            })

        log.info(f"[HackerNews] → {len(items)} posts")

    except Exception as e:
        log.error(f"[HackerNews] : {e}")

    return items


def _collect_hf_models(task="text-generation", limit=15):
    items = []

    try:
        resp = requests.get(
            "https://huggingface.co/api/models",
            params={
                "pipeline_tag": task,
                "sort": "lastModified",
                "direction": -1,
                "limit": limit
            },
            headers=HF_HEADERS,
            timeout=15
        )

        resp.raise_for_status()

        for m in resp.json():
            items.append({
                "source": "HuggingFace Hub",
                "type": "model",
                "title": m.get("modelId", ""),
                "url": f"https://huggingface.co/{m.get('modelId','')}",
                "summary": f"task:{task} | likes:{m.get('likes',0)} | downloads:{m.get('downloads',0)}",
                "task": task,
                "likes": m.get("likes", 0),
                "downloads": m.get("downloads", 0),
                "tags": m.get("tags", []),
                "published": m.get("lastModified", ""),
                "collected_at": datetime.now(timezone.utc).isoformat(),
            })

        log.info(f"[HF Models] {task} → {len(items)} modèles")

    except Exception as e:
        log.error(f"[HF Models] {e}")

    return items


def _collect_hf_papers(limit=20):
    items = []

    try:
        resp = requests.get(
            "https://huggingface.co/api/daily_papers",
            headers=HF_HEADERS,
            timeout=15
        )

        resp.raise_for_status()

        for paper in resp.json()[:limit]:

            p = paper.get("paper", {})

            items.append({
                "source": "HuggingFace Daily Papers",
                "type": "paper",
                "title": p.get("title", ""),
                "url": f"https://arxiv.org/abs/{p.get('id','')}",
                "summary": p.get("summary", "")[:400],
                "upvotes": paper.get("totalUpvotes", 0),
                "published": p.get("publishedAt", ""),
                "collected_at": datetime.now(timezone.utc).isoformat(),
            })

        log.info(f"[HF Papers] → {len(items)} papers")

    except Exception as e:
        log.error(f"[HF Papers] {e}")

    return items


def _save(data):

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    for fname in [f"dataset_{ts}.json", "dataset_latest.json"]:

        with open(DATA_DIR / fname, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    if data:
        with open(DATA_DIR / "dataset_latest.csv", "w", newline="", encoding="utf-8") as f:

            w = csv.DictWriter(
                f,
                fieldnames=list(data[0].keys()),
                extrasaction="ignore"
            )

            w.writeheader()
            w.writerows(data)

    sources = {
        "rss_blogs": RSS_SOURCES,
        "github": {
            "python/daily": "https://github.com/trending/python"
        },
        "hackernews": {
            "topstories": "https://hacker-news.firebaseio.com/v0/topstories.json"
        },
        "apis": {
            "HuggingFace Hub": "https://huggingface.co/api/models",
            "HuggingFace Papers": "https://huggingface.co/api/daily_papers"
        },
    }

    with open(DATA_DIR / "sources_surveillees.json", "w", encoding="utf-8") as f:
        json.dump(sources, f, ensure_ascii=False, indent=2)

    log.info(f"[SAVE] {len(data)} éléments → data/")


def collector_node(state: CollectorState) -> dict:

    log.info("=" * 50)
    log.info("  Nœud collector — démarrage")
    log.info("=" * 50)

    articles, repos, models, papers, hackernews_posts = [], [], [], [], []

    for name, url in RSS_SOURCES.items():
        articles.extend(_collect_rss(name, url))
        time.sleep(0.4)

    repos.extend(_collect_github_trending("python", "daily"))
    repos.extend(_collect_github_trending("jupyter-notebook", "weekly"))

    hackernews_posts.extend(_collect_hackernews())

    for task in ["text-generation", "image-to-text", "text-to-image"]:
        models.extend(_collect_hf_models(task))

    papers.extend(_collect_hf_papers())

    _save(articles + repos + models + papers + hackernews_posts)

    total = (
        len(articles)
        + len(repos)
        + len(models)
        + len(papers)
        + len(hackernews_posts)
    )

    log.info(f"  Nœud collector terminé — {total} éléments")

    return {
        "articles": articles,
        "repos": repos,
        "models": models,
        "papers": papers,
        "hackernews_posts": hackernews_posts,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "status": "done",
    }


def build_graph():

    graph = StateGraph(CollectorState)

    graph.add_node("collector", collector_node)

    graph.set_entry_point("collector")

    graph.add_edge("collector", END)

    return graph.compile()


if __name__ == "__main__":

    print("\n" + "=" * 50)
    print("  Veille Tech — Agent de collecte (Hamza)")
    print("=" * 50)

    print(f"\n  Clés API :")
    print(f"    GitHub       : {'✅ chargé' if GITHUB_TOKEN else '❌ absent (optionnel)'}")
    print(f"    HF           : {'✅ chargé' if HF_TOKEN else '❌ absent (optionnel)'}")
    print("    Hacker News  : ✅ API publique")

    print("\n  Démarrage...\n")

    final = build_graph().invoke({
        "articles": [],
        "repos": [],
        "models": [],
        "papers": [],
        "hackernews_posts": [],
        "collected_at": "",
        "status": "collecting",
        "analysis_result": {},
        "knowledge_base": {},
        "report": "",
    })

    print("\n" + "=" * 50)
    print("  RÉSULTATS FINAUX")
    print("=" * 50)

    print(f"  Articles RSS   : {len(final['articles'])}")
    print(f"  Repos GitHub   : {len(final['repos'])}")
    print(f"  Modèles HF     : {len(final['models'])}")
    print(f"  Papers HF      : {len(final['papers'])}")
    print(f"  Hacker News    : {len(final['hackernews_posts'])}")

    print(f"\n  Fichiers → data/dataset_latest.json")
    print(f"           → data/dataset_latest.csv")
    print(f"           → data/sources_surveillees.json")

    print("=" * 50 + "\n")