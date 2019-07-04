import os
import jieba
import wordcloud
import numpy as np
from PIL import Image


class WC:
    def __init__(
            self, img_path=None, font_path=None, width=None, height=None,
            background_color="white",
    ):
        self.img_path = img_path
        self.font_path = font_path
        self.width = width or 800
        self.height = height or 600
        self.background_color = background_color

        mask = None
        if self.img_path:
            mask = np.array(Image.open(self.img_path))

        self.wordcloud = wordcloud.WordCloud(
            width=self.width,
            height=self.height,
            background_color=self.background_color,
            font_path=self.font_path,
            mask=mask,
        )

    def generate(self, content=None, src=None, dest=None):
        if not content and not src:
            raise Exception("content or src must be set")

        if content and src:
            raise Exception("content and src can not be set both")

        if content and not dest:
            raise Exception("dest must be set")

        if src:
            dest = dest or os.path.splitext(src)[0] + ".png"
            with open(src, "r", encoding="utf8") as file:
                content = file.read()

        self.wordcloud.generate(" ".join(jieba.cut(content)))

        print(f"picture saved to {dest}")
        self.wordcloud.to_file(dest)


if __name__ == "__main__":
    text_path = "maple.txt"
    img_path = "/home/yuyy/Pictures/19399315_p0.jpg"
    font_path = "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc"

    wc = WC(img_path, font_path)
    wc.generate(src=text_path)
