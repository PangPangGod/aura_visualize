from abc import ABC, abstractmethod
from pydantic import BaseModel, validate_call
import os
import re

from wordcloud import WordCloud
from PIL import Image
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from konlpy.tag import Okt

from collections import Counter
from typing import List, Optional

class BaseVisualization(ABC, BaseModel):
    text: str

    def _analyze_text_okt(self):
        okt = Okt()
        text = self.text
        text = re.sub(r'\n', ' ', text)
        text = re.sub(r'[^가-힣\s]', '', text)

        nouns = okt.nouns(text)
        stop_words = ['활동', '학기', '학년', '제목', '생각', '모습', '내용', '의미', '특징', '대해', '대한', '통해', '위해', '또한',
                      '여자', '남자', '고등학교', '자신', '김소윤', '관련', '매우', '보임']  # 필요에 따라 조정 혹은 변수로 받아서 하도록..

        filtered_words = [word for word in nouns if len(word) > 1 and word not in stop_words]
        return Counter(filtered_words)
    
    @abstractmethod
    def visualize():
        pass

class BarChartVisualization(BaseVisualization):
    def get_config(self, title: str, font_path: Optional[str] = None, num_of_words: int = 25):
        if font_path is None:
            font_path = os.path.join(os.path.dirname(__file__), 'assets', 'SEOULNAMSANB.TTF')
        
        font = self._get_font_name(font_path)
        counter = self._analyze_text_okt()

        most_common_words = counter.most_common(num_of_words)
        items = [item for item, count in most_common_words]
        frequencies = [count for item, count in most_common_words]

        log_frequencies = np.log(frequencies)
        norm = plt.Normalize(min(log_frequencies), max(log_frequencies))
        colors = plt.cm.YlOrRd(norm(log_frequencies))

        config = {
            "font_path": font_path,
            "font": font,
            "items": items,
            "frequencies": frequencies,
            "figsize": (10, 6),
            "color": colors,
            "ylabel": '등장 횟수',
            "xticks_rotation": 45,
            "xticks_ha": 'right',
            "title": title,
            "text_offset": 0.1,
            "fontsize": 10
        }

        return config

    def visualize(self, chart_title:str = "빈도수 분석 결과", save_path:Optional[str] = "", file_name:Optional[str] = "bar_chart_with_words.png", font_path: Optional[str] = None, num_of_words: int = 25, **kwargs):
        config = self.get_config(title=chart_title, font_path=font_path, num_of_words=num_of_words)
        config.update(kwargs)
        
        plt.rcParams['font.family'] = config["font"]
        fig, ax = plt.subplots(figsize=config["figsize"])
        ax.set_title(config["title"])
        ax.bar(config["items"], config["frequencies"], color=config["color"])
        ax.set_ylabel(config["ylabel"])
        
        ax.set_xticks(range(len(config["items"])))
        ax.set_xticklabels(config["items"], rotation=config["xticks_rotation"], ha=config["xticks_ha"])

        for i, v in enumerate(config["frequencies"]):
            ax.text(i, v + config["text_offset"], str(v), ha='center', fontsize=config["fontsize"])

        plt.savefig(os.path.join(save_path, file_name), dpi=300, bbox_inches='tight')

    def _get_font_name(self, font_path: str):
        fname = fm.FontProperties(fname=font_path).get_name()
        fe = fm.FontEntry(font_path, name=fname)
        fm.fontManager.ttflist.insert(0, fe)
        return fname
    
class WordCloudVisualization(BaseVisualization):
    counter: Optional[Counter] = None

    @validate_call
    def visualize(self, save_path:Optional[str] = "", file_name:Optional[str] = "wordcloud.png", font_path: Optional[str] = None, mask_path: Optional[str] = None, relative_scaling: float = 0.3):
        if font_path is None:
            font_path = os.path.join(os.path.dirname(__file__), 'assets', 'SEOULNAMSANB.TTF')
        if mask_path is None:
            mask_path = os.path.join(os.path.dirname(__file__), 'assets', 'cloud.png')

        counter = self._analyze_text_okt()  # BaseVisualization의 메서드 사용
        filtered_words = {word: count for word, count in counter.items() if count >= 2}

        mask = self._get_mask(mask_path)

        wordcloud = WordCloud(
            font_path=font_path,
            width=900,
            height=600,
            max_font_size=150,
            min_font_size=10,
            max_words=100,
            background_color="White",
            mode="RGB",
            mask=mask,
            colormap='Dark2_r',
            relative_scaling=relative_scaling,
            prefer_horizontal=1.0,
        ).generate_from_frequencies(filtered_words)

        plt.figure(figsize=(15,10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)


        plt.savefig(os.path.join(save_path, file_name), dpi=300, bbox_inches='tight')

    def _color_func(self, word, font_size, position, orientation, random_state=None, **kwargs):
        """
        단어의 색상을 로그 스케일을 기반으로 지정하는 함수.
        
        Args:
            word (str): 워드 클라우드에서의 단어.
            font_size (int): 해당 단어의 폰트 크기.
            position (tuple): 단어의 위치 (x, y) 좌표.
            orientation (int): 단어의 방향 (horizontal or vertical).
            random_state (RandomState): 난수 생성기.
            **kwargs: 추가적인 인수들.
        
        Returns:
            tuple: RGB 색상 값.
        """

        if self.counter is None:
            raise ValueError("Counter has not been initialized")
        
        log_max = np.log(max(self.counter.values()))
        color_value = np.log(self.counter[word]) / log_max
        rgb = plt.cm.YlOrRd(color_value)[:3]
        return tuple(int(x*255) for x in rgb)
    
    @validate_call
    def _get_mask(self, path: str):
        return np.array(Image.open(path))