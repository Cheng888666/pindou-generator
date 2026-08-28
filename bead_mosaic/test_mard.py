from color_matcher import (
    load_color_database,
    prepare_color_database,
    find_nearest_color
)


print("========== MARD 221 测试 ==========")


colors = load_color_database()

print(
    "颜色数量：",
    len(colors)
)


prepared = prepare_color_database(
    colors
)


print(
    "预处理颜色数量：",
    len(prepared)
)


# 测试一个红色

test_rgb = [255, 0, 0]


color, distance = \
    find_nearest_color(
        test_rgb,
        prepared
    )


print(
    "测试 RGB：",
    test_rgb
)


print(
    "最接近 MARD 色号：",
    color["code"]
)


print(
    "MARD HEX：",
    color["hex"]
)


print(
    "Lab 距离：",
    distance
)


print(
    "==================================="
)