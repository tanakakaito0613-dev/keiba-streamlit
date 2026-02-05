import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    )
}

def get_race_info(url: str):
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    # レース基本情報
    race_name = soup.select_one(".RaceName")
    race_data = soup.select_one(".RaceData01")

    race_name = race_name.get_text(strip=True) if race_name else ""
    race_info = race_data.get_text(" ", strip=True) if race_data else ""

    horses = []

    table = soup.select_one("table.Shutuba_Table")
    if not table:
        return []

    rows = table.select("tr")[1:]  # ヘッダ除外

    for r in rows:
        cols = r.select("td")
        if len(cols) < 9:
            continue

        horses.append({
            "馬番": cols[1].get_text(strip=True),
            "馬名": cols[3].get_text(strip=True),
            "騎手": cols[6].get_text(strip=True),
            "斤量": cols[5].get_text(strip=True),
            "人気": None,  # 出馬表時点では無い
            "レース名": race_name,
            "レース条件": race_info
        })

    return horses
