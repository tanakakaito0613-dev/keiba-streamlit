import requests
from bs4 import BeautifulSoup

def text_or_none(el):
    return el.get_text(strip=True) if el else None

def normalize_weight(text):
    return float(text.replace("kg", "")) if text else None

def normalize_popularity(text):
    if not text:
        return None
    return int(text.replace("(", "").replace("番人気", "").replace(")", ""))

def normalize_sex_age(text):
    if not text:
        return None, None
    sex_age = text.split("/")[0]  # 牡6
    sex = sex_age[0]
    age = int(sex_age[1:])
    return sex, age

def parse_past_race(td):
    """td = row.select_one("td.past.p1")など"""
    if not td:
        return None

    date = text_or_none(td.select_one("div.date"))
    rc = text_or_none(td.select_one("div.rc"))
    race_name = text_or_none(td.select_one("div.race_line a"))
    grade = text_or_none(td.select_one("span.grade_icon"))
    place = text_or_none(td.select_one("div.place"))
    max_head = text_or_none(td.select_one("span.max"))
    gate = text_or_none(td.select_one("span.gate"))
    popularity = text_or_none(td.select_one("span.pop"))

    jockey = text_or_none(td.select_one("div.info_line1 div.jockey"))
    weight = normalize_weight(text_or_none(td.select_one("div.info_line1 div.weight")))
    dist = text_or_none(td.select_one("div.info_line2 span.dist"))
    condition = text_or_none(td.select_one("div.info_line2 span.condition"))
    rating = text_or_none(td.select_one("div.info_line2 p.rating"))
    h_weight = text_or_none(td.select_one("div.info_line2 p.h_weight"))
    corner = [li.get_text(strip=True) for li in td.select("div.corner_list ul li")]
    f3 = text_or_none(td.select_one("div.f3"))
    fin = text_or_none(td.select_one("p.fin"))

    return {
        "日付": date,
        "競馬場": rc,
        "レース名": race_name,
        "グレード": grade,
        "着順": place,
        "頭数": max_head,
        "枠番": gate,
        "人気": popularity,
        "騎手": jockey,
        "斤量": weight,
        "距離": dist,
        "馬場状態": condition,
        "レーティング": rating,
        "馬体重": h_weight,
        "コーナー通過": corner,
        "3F": f3,
        "上がり差": fin
    }


def get_race_info(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers, timeout=10)
    res.raise_for_status()
    res.encoding = "cp932"  # JRA公式

    soup = BeautifulSoup(res.text, "html.parser")

    # レース基本情報
    race_table = soup.select_one("table.basic.narrow-xy.mt20")
    if not race_table:
        return None

    race_header = race_table.select_one("caption div.race_header")
    race_name_tag = race_header.select_one("span.race_name")
    race_name = race_name_tag.find(text=True, recursive=False).strip()
    date_place = race_header.select_one("div.date_line .date").get_text(strip=True)
    # 開催競馬場は日付文字列の中にある「東京」などを抽出
    import re
    place_match = re.search(r"(札幌|函館|福島|新潟|東京|中山|中京|京都|阪神|小倉)", date_place)
    place = place_match.group(0) if place_match else None
    course_info = race_header.select_one("div.cell.course").get_text(strip=True)
    distance_match = re.search(r"(\d+),?(\d*)\s*メートル", course_info)
    distance = int(distance_match.group(1) + (distance_match.group(2) or "")) if distance_match else None
    match = re.search(r"(芝|ダート)\s*[・,]\s*(右|左)", course_info)
    if match:
        track_type = match.group(1)       # 芝 or ダート
        track_direction = match.group(2)  # 右 or 左
    else:
        track_type, track_direction = None, None
        print("抽出できませんでした")

    horses = []
    
    for row in soup.select("tr"):
        horse_name = row.select_one("td.horse div.name a")
        if not horse_name:
            continue  # 出馬表以外は除外

        waku_img = row.select_one("td.waku img")
        sex, age = normalize_sex_age(text_or_none(row.select_one("td.jockey p.age")))

        horse = {
            "枠": waku_img["alt"] if waku_img else None,
            "馬番": int(text_or_none(row.select_one("td.num"))),
            "馬名": text_or_none(horse_name),

            "オッズ": float(text_or_none(row.select_one("div.odds strong")) or 0),
            "人気": normalize_popularity(text_or_none(row.select_one("span.pop_rank"))),

            "性": sex,
            "年齢": age,
            "斤量": normalize_weight(text_or_none(row.select_one("td.jockey p.weight"))),
            "騎手": text_or_none(row.select_one("td.jockey p.jockey a")),

            "父": text_or_none(row.select_one("ul.family_line li.sire")).replace("父：", "") if row.select_one("ul.family_line li.sire") else None,
            "母": text_or_none(row.select_one("ul.family_line li.mare")).replace("母：", "") if row.select_one("ul.family_line li.mare") else None,
            
            # レース情報
            "レース名": race_name,
            "開催競馬場": place,
            "距離": distance,
            "馬場形態": track_type,
            "方向": track_direction,

            # 過去3走
            "過去走": [
                parse_past_race(row.select_one("td.past.p1")),
                parse_past_race(row.select_one("td.past.p2")),
                parse_past_race(row.select_one("td.past.p3")),
            ],
        }

        horses.append(horse)

    return horses
