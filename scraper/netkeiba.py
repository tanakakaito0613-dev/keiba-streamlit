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

def safe_text(cols, idx):
    return cols[idx].get_text(strip=True) if len(cols) > idx else None

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
    
    for row in table.select("tr.HorseList"):
        try:
            waku = row.select_one("td[class^=Waku]")
            umaban = row.select_one("td[class^=Umaban]")
            horse_anchor = row.select_one("span.HorseName a")
            sex_age = row.select_one("td.Barei")
            sex, age = None, None
            
            if sex_age:
                t = sex_age.get_text(strip=True)
                sex = t[0]
                age = t[1:]
                
        weight_el = row.select_one("td.Dredging")
        jockey_el = row.select_one("td.Jockey a")
        odds_el = row.select_one("td.Popular span")
        ninki_el = row.select_one("td.Popular_Ninki span")
        
        def clean(v):
            return None if not v or v in ("--", "**", "---.-") else v
            
    
        # 血統
        sire = mare = None
        blood_td = row.select_one("td.Blood")
        if blood_td:
            lines = blood_td.get_text("\n", strip=True).split("\n")
            if len(lines) >= 2:
                sire, mare = lines[0], lines[1]

        # 過去走
        past_race_list = []
        past_table = row.find_next("table", class_="RaceTable02")
        if past_table:
            for pr in past_table.select("tr")[1:]:
                tds = pr.select("td")
                if len(tds) >= 7:
                    past_race_list.append({
                        "日付": tds[0].get_text(strip=True),
                        "競馬場": tds[1].get_text(strip=True),
                        "距離": tds[3].get_text(strip=True),
                        "馬場状態": tds[4].get_text(strip=True),
                        "着順": tds[5].get_text(strip=True),
                        "頭数": tds[6].get_text(strip=True)
                    })

        horses.append({
            "枠": waku.get_text(strip=True) if waku else None,
            "馬番": umaban.get_text(strip=True) if umaban else None,
            "馬名": horse_anchor.get_text(strip=True) if horse_anchor else None,
            "性": sex,
            "年齢": age,
            "斤量": weight_el.get_text(strip=True) if weight_el else None,
            "騎手": jockey_el.get_text(strip=True) if jockey_el else None,
            "オッズ": clean(odds_el.get_text(strip=True)) if odds_el else None,
            "人気": clean(ninki_el.get_text(strip=True)) if ninki_el else None,
            "父": sire,
            "母": mare,
            "過去走": past_race_list
        })

    except Exception as e:
        print("skip horse:", e)

