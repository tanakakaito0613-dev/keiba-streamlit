import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Referer": "https://race.netkeiba.com/"
}

def clean(v):
    return None if not v or v in ("--", "**", "---.-") else v


def get_race_info(race_id: str):
    """
    出馬表（枠・馬番・馬名・性齢・斤量・騎手）を確実に取得
    """
    url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}"
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    res.encoding = "EUC-JP"

    soup = BeautifulSoup(res.text, "html.parser")

    table = soup.select_one("table.Shutuba_Table")
    if not table:
        print("❌ Shutuba_Table not found")
        return []

    horses = []

    rows = table.select("tr.HorseList")
    print("DEBUG HorseList rows:", len(rows))

    for row in table.select("tr.HorseList"):
        cols = row.select("td")
        if len(cols) < 7:
            continue

        sex_age = cols[4].get_text(strip=True)

        horses.append({
            "枠": cols[0].get_text(strip=True),
            "馬番": cols[1].get_text(strip=True),
            "馬名": cols[3].select_one("a").get_text(strip=True),
            "性": sex_age[0],
            "年齢": sex_age[1:],
            "斤量": cols[5].get_text(strip=True), 
            "騎手": cols[6].get_text(strip=True),
            })


    return horses
