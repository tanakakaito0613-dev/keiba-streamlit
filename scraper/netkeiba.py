import requests
import streamlit as st
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Referer": "https://race.netkeiba.com/"
}

def get_race_info(url: str):
    # newspaper.html を前提
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    res.encoding = "EUC-JP"
    st.write(res.text[:300])
    soup = BeautifulSoup(res.text, "html.parser")

    # 出馬表テーブル
    table = soup.select_one("table.Shutuba_Table")
    if not table:
        print("❌ Shutuba_Table not found")
        return []

    horses = []


    # ===== 出馬表の各馬の基本情報 =====
    for row in table.select("tr.HorseList"):
        try:
            # 枠
            waku_td = row.find("td", class_=lambda c: c and c.startswith("Waku"))
            waku = waku_td.get_text(strip=True) if waku_td else None

            # 馬番
            uma_td = row.find("td", class_=lambda c: c and c.startswith("Umaban"))
            umaban = uma_td.get_text(strip=True) if uma_td else None

            # 馬名
            horse_anchor = row.select_one("span.HorseName a")
            horse_name = horse_anchor.get_text(strip=True) if horse_anchor else None

            # 性・年齢
            sex_age = row.select_one("td.Barei")
            sex = None
            age = None
            if sex_age:
                sa_txt = sex_age.get_text(strip=True)
                sex = sa_txt[0] if sa_txt else None
                age = sa_txt[1:] if sa_txt and len(sa_txt) > 1 else None

            # 斤量
            weight_el = row.select_one("td.Txt_C")
            weight = weight_el.get_text(strip=True) if weight_el else None

            # 騎手
            jockey_el = row.select_one("td.Jockey a")
            jockey = jockey_el.get_text(strip=True) if jockey_el else None

            # オッズ（newsでは載ってない可能性あり）
            odds = None
            odds_el = row.select_one("td.Popular span")
            if odds_el:
                odds = odds_el.get_text(strip=True)

            # 人気
            nin_el = row.select_one("td.Popular_Ninki span")
            ninki = nin_el.get_text(strip=True) if nin_el else None

            # index マップ用
            idx = umaban

            # ===== 馬柱（過去走） =====
            # newspaper.html 上で馬柱がまとまっている
            # 馬柱のテーブルは .HorseList を index で分ける
            # ここでは馬柱IDに umaban が使われている
            past_race_list = []
            horse_row_in_past = soup.select_one(f"table#race_history{idx}")
            if horse_row_in_past:
                for pr in horse_row_in_past.select("tr")[1:]:
                    tds = pr.select("td")
                    if len(tds) > 6:
                        past_race_list.append({
                            "日付": tds[0].get_text(strip=True),
                            "競馬場": tds[1].get_text(strip=True),
                            "距離": tds[3].get_text(strip=True),
                            "馬場状態": tds[4].get_text(strip=True),
                            "着順": tds[5].get_text(strip=True),
                            "頭数": tds[6].get_text(strip=True)
                        })

            # ===== 血統（父・母） =====
            # blood_table が載っている
            sire = None
            mare = None
            blood_table = soup.select_one(f"table#blood_table{idx}")
            if blood_table:
                cells = blood_table.select("td")
                if len(cells) >= 4:
                    sire = cells[0].get_text(strip=True)
                    mare = cells[3].get_text(strip=True)

            horse = {
                "枠": waku,
                "馬番": umaban,
                "馬名": horse_name,
                "性": sex,
                "年齢": age,
                "斤量": weight,
                "騎手": jockey,
                "オッズ": odds,
                "人気": ninki,
                "父": sire,
                "母": mare,
                "過去走": past_race_list
            }

            horses.append(horse)

        except Exception as e:
            print("skip horse:", e)

    return horses

