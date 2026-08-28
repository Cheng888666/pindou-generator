import json
import os
import numpy as np

from skimage.color import rgb2lab


# =========================
# 找到项目根目录
# =========================

def get_project_root():

    return os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )


# =========================
# 加载 MARD 221
# =========================

def load_color_database():

    root = get_project_root()

    color_file = os.path.join(
        root,
        "data",
        "mard_221.json"
    )

    with open(
        color_file,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    # 正式 MARD JSON 是一个对象
    if isinstance(data, dict):

        colors = data["colors"]

    else:

        colors = data

    print(
        f"MARD 色库加载成功：{len(colors)} 色"
    )

    return colors


# =========================
# RGB → Lab
# =========================

def rgb_to_lab(rgb):

    arr = np.array(
        [[rgb]],
        dtype=np.float32
    ) / 255.0

    lab = rgb2lab(arr)

    return lab[0, 0]


# =========================
# 预处理 MARD 色库
# =========================

def prepare_color_database(colors):

    prepared = []

    for color in colors:

        rgb = np.array(
            color["rgb"],
            dtype=np.float32
        )

        lab = rgb_to_lab(rgb)

        prepared.append({

            "code":
                color["code"],

            "hex":
                color["hex"],

            "rgb":
                color["rgb"],

            "group":
                color.get(
                    "group",
                    ""
                ),

            "lab":
                lab

        })

    return prepared


# =========================
# 最近颜色
# =========================

def find_nearest_color(
    rgb,
    prepared_colors
):

    lab = rgb_to_lab(rgb)

    best_color = None

    best_distance = float("inf")


    for color in prepared_colors:

        distance = np.linalg.norm(
            lab - color["lab"]
        )

        if distance < best_distance:

            best_distance = distance

            best_color = color


    return best_color, best_distance


# =========================
# 整张图片颜色匹配
# =========================

def match_image(
    image,
    prepared_colors
):

    image = image.convert("RGB")

    width, height = image.size

    pixels = np.array(image)

    pattern = []

    statistics = {}


    for y in range(height):

        row = []

        for x in range(width):

            rgb = pixels[y, x]

            color, distance = \
                find_nearest_color(
                    rgb,
                    prepared_colors
                )

            code = color["code"]

            row.append(code)


            if code not in statistics:

                statistics[code] = {

                    "code":
                        code,

                    "hex":
                        color["hex"],

                    "rgb":
                        color["rgb"],

                    "group":
                        color["group"],

                    "count":
                        0

                }


            statistics[code]["count"] += 1


        pattern.append(row)


    # 按使用数量排序

    statistics_list = sorted(
        statistics.values(),
        key=lambda x: x["count"],
        reverse=True
    )


    return (
        pattern,
        statistics_list
    )