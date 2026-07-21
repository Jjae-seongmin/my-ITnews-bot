import os
import json
import html
import feedparser
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

FEEDS = {
    "전자신문 AI": "http://rss.etnews.com/04046.xml",
    "전자신문 IT": "http://rss.etnews.com/03.xml",
    "AI타임스": "https://www.aitimes.com/rss/allArticle.xml",
}
COUNT = 4
SENT_FILE = "sent.json"
MAX_HISTORY = 500  # 기록을 무한정 쌓지 않기 위한 상한


def load_sent():
    """이전에 보낸 링크 목록을 불러온다. 파일이 없으면 빈 목록."""
    if not os.path.exists(SENT_FILE):
        return []
    with open(SENT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_sent(links):
    """최근 MAX_HISTORY개만 남기고 저장한다."""
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(links[-MAX_HISTORY:], f, ensure_ascii=False, indent=2)


def fetch_articles():
    articles = []
    for source, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                print(f"[경고] {source}: 기사 없음, 건너뜀")
                continue
            for entry in feed.entries[:COUNT]:
                articles.append({
                    "source": source,
                    "title": entry.title.strip(),
                    "link": entry.link,
                })
        except Exception as e:
            print(f"[에러] {source}: {e}")
            continue
    return articles


def build_message(articles):
    lines = ["📰 <b>오늘의 IT 뉴스</b>", ""]
    for a in articles:
        title = html.escape(a["title"])
        lines.append(f"• [{a['source']}] <a href=\"{a['link']}\">{title}</a>")
    return "\n".join(lines)


def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    })
    res.raise_for_status()
    return res.json()


def main():
    sent = load_sent()
    sent_set = set(sent)  # 조회 속도를 위해 set으로 변환

    articles = fetch_articles()
    new_articles = [a for a in articles if a["link"] not in sent_set]

    if not new_articles:
        print("새 기사가 없습니다. 발송 생략.")
        return

    send_telegram(build_message(new_articles))

    # 발송에 성공한 뒤에 기록한다 (실패했는데 기록하면 기사를 영영 놓침)
    sent.extend(a["link"] for a in new_articles)
    save_sent(sent)
    print(f"{len(new_articles)}건 발송 완료")


if __name__ == "__main__":
    main()