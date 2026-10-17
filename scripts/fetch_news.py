import os
import datetime
import requests
from bs4 import BeautifulSoup
from google import genai

def fetch_raw_news():
    """ニュースサイトから情報を取得（例としてRSSや特定のHTMLをパース）"""
    # ここに対象のニュースサイトのURLやRSSを入力します
    url = "https://magazine.algomatic.jp" 
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "xml")
    
    items = soup.find_all("item")
    news_text = ""
    for item in items[:5]: # 上位5件
        title = item.title.text
        link = item.link.text
        news_text += f"- タイトル: {title}\n  URL: {link}\n"
    return news_text

def summarize_with_gemini(raw_text):
    """Gemini APIを使用して、Obsidian（Markdown）形式に要約・整形"""
    # 環境変数からAPIキーを自動読み込み
    client = genai.Client()
    
    prompt = f"""
    以下のニュース情報を取得しました。
    Obsidianのノートとして最適なMarkdown形式で、重要度別に整理・要約してください。
    各ニュースに対して、1行の要約と、なぜ重要なのかの背景を箇条書きで追加してください。
    
    # ニュースデータ
    {raw_text}
    """
    
    # 無料枠で利用可能な最新の推奨モデルを使用
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
    )
    return response.text

def save_to_vault(content):
    """ObsidianのVault（例: 日記フォルダなど）に保存"""
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # Vault内の保存先フォルダ（パスは環境に合わせて調整してください）
    # 例: "DailyNotes/2026-10-15.md" 
    folder_path = "DailyNotes"
    os.makedirs(folder_path, exist_ok=True)
    
    file_path = os.path.join(folder_path, f"{today}.md")
    
    # 既存のファイルがある場合は追記、なければ新規作成
    mode = "a" if os.path.exists(file_path) else "w"
    with open(file_path, mode, encoding="utf-8") as f:
        f.write("\n\n## 🤖 AI Daily News Summary\n")
        f.write(content)
    print(f"Saved news to {file_path}")

if __name__ == "__main__":
    print("Fetching news...")
    raw_news = fetch_raw_news()
    
    print("Processing with Gemini...")
    summary = summarize_with_gemini(raw_news)
    
    print("Saving to Vault...")
    save_to_vault(summary)
    print("Done!")
