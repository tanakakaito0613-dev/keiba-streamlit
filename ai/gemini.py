from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def score_horse(horse):
    """
    馬ごとの適性を過去走からスコア化
    """
    course_scores = {}
    distance_scores = {}
    track_scores = {"良": 0, "稍重": 0, "重": 0, "不良": 0}

    past_races = horse.get("過去走", [])

    for race in past_races:
        rank = race.get("着順")
        if not isinstance(rank, int):
            continue

        finish_score = 10 if rank == 1 else 8 if rank == 2 else 6 if rank == 3 else 3

        course = race.get("競馬場")
        if course:
            course_scores[course] = max(course_scores.get(course, 0), finish_score)

        dist = race.get("距離")
        if dist:
            distance_scores[dist] = max(distance_scores.get(dist, 0), finish_score)

        track = race.get("馬場状態")
        if track in track_scores:
            track_scores[track] = max(track_scores[track], finish_score)

    horse["コース適性"] = course_scores
    horse["距離適性"] = distance_scores
    horse["馬場適性"] = track_scores

    return horse


def analyze_race(horses):
    if not horses:
        return "馬データが取得できませんでした。"

    # スコア計算
    for i in range(len(horses)):
        horses[i] = score_horse(horses[i])

    # プロンプト
    prompt = (
        "あなたは競馬予想の専門家です。\n"
        "以下の出走馬情報をもとに、血統と過去走適性を重視して全頭評価してください。\n"
        "最後に「本命・対抗・穴」を挙げ、単勝・複勝・馬連・3連複・3連単（ヒモ5頭程度）を提案してください。\n"
    )

    for h in horses:
        prompt += (
            f"\n馬番:{h.get('馬番','?')} "
            f"馬名:{h.get('馬名','?')} "
            f"性齢:{h.get('性','?')}{h.get('年齢','?')} "
            f"斤量:{h.get('斤量','?')} "
            f"騎手:{h.get('騎手','?')}\n"
            f"父:{h.get('父','不明')} 母:{h.get('母','不明')}\n"
            f"コース適性:{h.get('コース適性',{})}\n"
            f"距離適性:{h.get('距離適性',{})}\n"
            f"馬場適性:{h.get('馬場適性',{})}\n"
        )

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt,
    )

    return response.text
