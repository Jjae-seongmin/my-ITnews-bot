import feedparser

CANDIDATES = {
    "전자신문 AI": "http://rss.etnews.com/04046.xml",
    "전자신문 IT": "http://rss.etnews.com/03.xml",
    "전자신문 SW": "http://rss.etnews.com/04.xml",
    "AI타임스": "https://www.aitimes.com/rss/allArticle.xml",
    "바이라인네트워크": "https://byline.network/feed/",
    # 여기에 직접 찾은 주소를 계속 추가해보세요
}

for name, url in CANDIDATES.items():
    feed = feedparser.parse(url)
    count = len(feed.entries)
    if count == 0:
        print(f"❌ {name}: 기사 0건 (주소가 틀렸거나 차단됨)")
    else:
        print(f"✅ {name}: {count}건 | 최신: {feed.entries[0].title[:40]}")