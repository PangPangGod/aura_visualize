import streamlit as st
import os
from aura.visualize import BarChartVisualization, WordCloudVisualization

st.title("텍스트 시각화 도구")

text_input = st.text_area("텍스트를 입력하세요", height=200)
visualize_option = st.selectbox("시각화 유형 선택", ["Bar Chart", "Word Cloud"])
font_path = os.path.join('aura', 'assets', 'SEOULNAMSANB.TTF')
mask_path = os.path.join('aura', 'assets', 'cloud.png')

if st.button("시각화 생성"):
    if text_input.strip() == "":
        st.warning("텍스트를 입력하세요.")
    else:
        if visualize_option == "Bar Chart":
            bar_chart = BarChartVisualization(text=text_input)
            bar_chart.visualize(chart_title="빈도수 분석 결과", save_path="", file_name="bar_chart.png", font_path=font_path)

            st.image("bar_chart.png")
            with open("bar_chart.png", "rb") as f:
                st.download_button("Download Bar Chart", data=f, file_name="bar_chart.png", mime="image/png")

        elif visualize_option == "Word Cloud":
            word_cloud = WordCloudVisualization(text=text_input)
            word_cloud.visualize(save_path="", file_name="wordcloud.png", font_path=font_path, mask_path=mask_path)

            st.image("wordcloud.png")
            with open("wordcloud.png", "rb") as f:
                st.download_button("Download Word Cloud", data=f, file_name="wordcloud.png", mime="image/png")