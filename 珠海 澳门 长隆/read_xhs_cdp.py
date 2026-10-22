"""Read visible travel notes from the dedicated local CDP browser; do not export login state."""
import sys, json, argparse
from pathlib import Path
sys.path.insert(0, r'D:\travel\海拉尔\.ui-tools')
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
parser = argparse.ArgumentParser()
parser.add_argument('--url')
parser.add_argument('--save', default='xhs-browser-check')
args = parser.parse_args()
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222', no_defaults=True)
    pages = [page for page in browser.contexts[0].pages if 'xiaohongshu.com' in page.url]
    page = pages[-1] if pages else browser.contexts[0].new_page()
    if args.url:
        page.goto(args.url, wait_until='domcontentloaded', timeout=45000)
        page.wait_for_timeout(3000)
    data = {'url': page.url, 'title': page.title(), 'text': page.locator('body').inner_text(),
            'links': page.locator('a[href*="/explore/"], a[href*="/search_result/"]').evaluate_all('(els) => els.map(a => ({text:a.innerText,url:a.href}))')}
    folder = ROOT / 'research'
    folder.mkdir(exist_ok=True)
    (folder / (args.save + '.json')).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(data, ensure_ascii=False)[:18000])
    # Exit the connection without closing the user's browser.
