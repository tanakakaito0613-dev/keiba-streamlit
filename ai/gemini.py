from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def score_horse(horse):
    """
    馬ごとのコース・距離・馬場適性を過去走からスコア化する
    """
    course_scores = {}
    distance_scores = {}
    track_scores = {"良":0, "稍重":0, "重":0, "不良":0}

    past_races = horse.get('過去走', [])

    for race in past_races:
        # 着順に応じたスコア
        finish_score = 10 if race['着順']==1 else 8 if race['着順']==2 else 6 if race['着順']==3 else 3

        # コース適性
        course = race['競馬場']
        course_scores[course] = max(course_scores.get(course, 0), finish_score)

        # 距離適性
        dist = race['距離']
        distance_scores[dist] = max(distance_scores.get(dist, 0), finish_score)

        # 馬場適性
        track = race['馬場状態']
        track_scores[track] = max(track_scores.get(track, 0), finish_score)

    horse['コース適性'] = course_scores
    horse['距離適性'] = distance_scores
    horse['馬場適性'] = track_scores

    return horse

def analyze_race(horses):
    if not horses:
        return "馬データが取得できませんでした。スクレイピング結果を確認してください。"

    # 各馬にスコアを計算
    for i in range(len(horses)):
        horses[i] = score_horse(horses[i])

    # プロンプト作成
    prompt = "あなたは競馬予想の専門家です。\n"
    prompt += "以下の出走馬情報をもとに、血統と馬場適性を重視して勝つ可能性が高い馬を理由付きで全頭予想してください。\n"
    prompt += "最後に「本命・対抗・穴」を挙げて単勝、複勝、馬連、3連複、3連単（ヒモを5頭程度）を予想してください。\n"

    for h in horses:
        prompt += f"\n{h['レース名']} {h['開催競馬場']} {h['馬場形態']} {h['方向']}回り {h['距離']}m\n"
        prompt += f"\n馬番:{h['馬番']} 馬名:{h['馬名']}"
        prompt += f" 性別:{h.get('性別','不明')} 年齢:{h.get('年齢','不明')} 斤量:{h.get('斤量','不明')}"
        prompt += f" 騎手:{h.get('騎手','不明')}"
        prompt += f" 父:{h.get('父','不明')} 母:{h.get('母','不明')}"
        prompt += f" コース適性:{h['コース適性']}"
        prompt += f" 距離適性:{h['距離適性']}"
        prompt += f" 馬場適性:{h['馬場適性']}\n"

    # AIに送信
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt,
    )

    return response.text

