# scraper/netkeiba.py
import requests
from bs4 import BeautifulSoup

def get_race_info(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://race.netkeiba.com/"
    }

    res = requests.get(url, headers=headers, timeout=10)
    res.raise_for_status()
    res.encoding = "EUC-JP"

    soup = BeautifulSoup(res.text, "html.parser")

    table = soup.select_one("table.Shutuba_Table")
    if not table:
        print("❌ Shutuba_Table not found")
        return []

    horses = []

    for row in table.select("tr.HorseList"):
        try:
            waku_td = row.find("td", class_=lambda x: x and x.startswith("Waku"))
            umaban_td = row.find("td", class_=lambda x: x and x.startswith("Umaban"))

            horse = {
                "枠": waku_td.get_text(strip=True) if waku_td else None,
                "馬番": umaban_td.get_text(strip=True) if umaban_td else None,
                "馬名": row.select_one(".HorseName a").get_text(strip=True),
                "性": row.select_one(".Barei").get_text(strip=True)[0],
                "年齢": row.select_one(".Barei").get_text(strip=True)[1:],
                "斤量": row.select_one("td.Txt_C").get_text(strip=True),
                "騎手": row.select_one(".Jockey a").get_text(strip=True),
                "オッズ": row.select_one(".Popular span").get_text(strip=True),
                "人気": row.select_one(".Popular_Ninki span").get_text(strip=True),
                "過去走": []
            }

            horses.append(horse)

        except Exception as e:
            print("skip horse:", e)

    return horses
