import streamlit as st
from scraper.netkeiba import get_race_info
from ai.gemini import analyze_race
import pandas as pd

st.set_page_config(page_title="競馬予想AI", page_icon="🏇")
st.title("🏇 競馬予想AI")

# URL入力
url = st.text_input("レースURLを入力（netkeibaから取得してください）", "")

if st.button("予想する") and url:
    with st.spinner("出馬表を取得中…"):
        horses = get_race_info(url)
        
    if not horses:
        st.warning("出馬表が取得できませんでした。URLを確認してください。")
    else:
        st.markdown("### 🏇 出馬表")
        horses_display = []
        for h in horses:
            h_copy = h.copy()
            h_copy['枠'] = h_copy.get('枠', '').replace("枠", "")
            h_copy["過去走"] = "\n".join([f"{r['日付']} {r['レース名']} {r['着順']}" for r in h['過去走']])
            horses_display.append(h_copy)
        df = pd.DataFrame(horses_display)
        st.dataframe(df[["枠", "馬番", "馬名", "オッズ", "人気", "性", "年齢", "斤量", "騎手", "父", "母", "過去走"]])

        with st.spinner("AIが予想中…"):
            result = analyze_race(horses)

        st.markdown("### 🤖 AI予想")
        st.write(result)


        st.success("予想完了！")








