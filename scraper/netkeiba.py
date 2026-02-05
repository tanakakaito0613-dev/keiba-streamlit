import requests
import streamlit as st
from bs4 import BeautifulSoup
import time

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
    res.encoding = "EUC-JP"
    st.write("status:", res.status_code)
    st.write("length:", len(res.text))
    st.write(res.text[1000:])
    
    soup = BeautifulSoup(res.text, "html.parser")

    horses = []

    table = soup.select_one("table.Shutuba_Table")
    if not table:
        return []

    rows = table.select("tr")[1:]  # ヘッダ除外

    for row in rows:
        cols = row.select("td")
        if len(cols) < 18:
            continue

        # 馬詳細ページURL
        horse_link = cols[3].select_one("a")
        horse_url = horse_link["href"] if horse_link else None
        if horse_url and horse_url.startswith("/"):
            horse_url = "https://db.netkeiba.com" + horse_url

        waku = cols[0].get_text(strip=True)
        if not waku:
            continue

        horse = {
            "枠": waku,
            "馬番": cols[1].get_text(strip=True),
            "馬名": cols[3].get_text(strip=True),
            "オッズ": cols[9].get_text(strip=True),
            "人気": cols[10].get_text(strip=True),
            "性": cols[4].get_text(strip=True)[0],
            "年齢": cols[4].get_text(strip=True)[1:],
            "斤量": cols[5].get_text(strip=True),
            "騎手": cols[6].get_text(strip=True),
            "父": "",
            "母": "",
            "過去走": []
        }

        # -------------------------
        # 馬詳細ページ（血統・過去走）
        # -------------------------
        if horse_url:
            try:
                time.sleep(0.5)  # アクセス抑制
                h_res = requests.get(horse_url, headers=HEADERS, timeout=10)
                h_soup = BeautifulSoup(h_res.text, "html.parser")

                # 血統
                pedigree = h_soup.select("table.blood_table tr td")
                if len(pedigree) >= 4:
                    horse["父"] = pedigree[0].get_text(strip=True)
                    horse["母"] = pedigree[3].get_text(strip=True)

                # 過去走（直近5走）
                race_rows = h_soup.select("table.db_h_race_results tr")[1:6]
                for r in race_rows:
                    tds = r.select("td")
                    if len(tds) < 11:
                        continue
                    horse["過去走"].append({
                        "日付": tds[0].get_text(strip=True),
                        "レース名": tds[4].get_text(strip=True),
                        "着順": tds[11].get_text(strip=True)
                    })

            except Exception:
                pass

        horses.append(horse)
    return horses






