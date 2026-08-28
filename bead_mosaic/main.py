from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from PIL import Image
import io
import base64

from color_matcher import (
    load_color_database,
    prepare_color_database,
    match_image
)


app = FastAPI()
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# 启动时加载 MARD 221
# =========================

print("正在加载 MARD 221 色库...")

mard_colors = load_color_database()

prepared_colors = prepare_color_database(
    mard_colors
)

print(
    f"MARD 221 色库准备完成："
    f"{len(prepared_colors)} 色"
)


# =========================
# 首页
# =========================

@app.get("/")
def home():

    return {
        "message":
            "拼豆图纸生成器后端运行正常",

        "mard_colors":
            len(prepared_colors)
    }


# =========================
# 图片生成
# =========================

@app.post("/generate")
async def generate(

    image: UploadFile = File(...),

    width: int = Form(100),

    height: int = Form(100),

    color_count: int = Form(221)
):

    print(
        f"\n收到图片："
        f"{image.filename}"
    )

    print(
        f"目标尺寸："
        f"{width} × {height}"
    )


    # =========================
    # 1. 读取原图
    # =========================

    contents = await image.read()

    original_image = Image.open(
        io.BytesIO(contents)
    ).convert("RGB")


    original_width, original_height = \
        original_image.size


    print(
        f"原图尺寸："
        f"{original_width} × "
        f"{original_height}"
    )


    # =========================
    # 2. 缩放
    # =========================

    mosaic = original_image.resize(
        (width, height),
        Image.Resampling.LANCZOS
    )


    # =========================
    # 3. MARD 221 颜色匹配
    # =========================

    print(
        "开始进行 MARD 221 "
        "颜色匹配..."
    )


    pattern, statistics = match_image(
        mosaic,
        prepared_colors
    )


    print(
        f"颜色匹配完成，"
        f"使用 {len(statistics)} 种颜色"
    )


    # =========================
    # 4. 根据匹配结果生成图像
    # =========================

    pattern_image = Image.new(
        "RGB",
        (width, height)
    )


    pixels = pattern_image.load()


    # 建立色号 → RGB 映射

    color_map = {}

    for color in prepared_colors:

        color_map[
            color["code"]
        ] = tuple(
            color["rgb"]
        )


    for y in range(height):

        for x in range(width):

            code = pattern[y][x]

            pixels[x, y] = \
                color_map[code]


    # =========================
    # 5. 放大用于网页显示
    # =========================

    display_scale = 10

    display_image = pattern_image.resize(

        (
            width * display_scale,
            height * display_scale
        ),

        Image.Resampling.NEAREST

    )


    # =========================
    # 6. 转 PNG
    # =========================

    buffer = io.BytesIO()

    display_image.save(
        buffer,
        format="PNG"
    )

    buffer.seek(0)


    pattern_base64 = \
        base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")


    # =========================
    # 7. 原始马赛克也保留
    # =========================

    mosaic_display = mosaic.resize(

        (
            width * display_scale,
            height * display_scale
        ),

        Image.Resampling.NEAREST

    )


    mosaic_buffer = io.BytesIO()

    mosaic_display.save(
        mosaic_buffer,
        format="PNG"
    )

    mosaic_buffer.seek(0)


    mosaic_base64 = \
        base64.b64encode(
            mosaic_buffer.getvalue()
        ).decode("utf-8")


    # =========================
    # 8. 返回前端
    # =========================

    return {

        "success": True,

        "filename":
            image.filename,

        "original_width":
            original_width,

        "original_height":
            original_height,

        "width":
            width,

        "height":
            height,

        "color_count":
            len(statistics),

        "mosaic":
            "data:image/png;base64,"
            + mosaic_base64,

        "pattern":
            pattern,

        "pattern_image":
            "data:image/png;base64,"
            + pattern_base64,

        "statistics":
            statistics,

        "total_beads":
            width * height
    }

# =========================
# 新增：导出 PNG（直接返回图纸PNG）
# =========================

@app.post("/export-png")
async def export_png(

    image: UploadFile = File(...),

    width: int = Form(100),

    height: int = Form(100),

    cell_size: int = Form(32)
):

    # 读取图片并转为拼豆图纸
    contents = await image.read()

    original_image = Image.open(
        io.BytesIO(contents)
    ).convert("RGB")

    mosaic = original_image.resize(
        (width, height),
        Image.Resampling.LANCZOS
    )

    # 颜色匹配
    pattern, statistics = match_image(
        mosaic,
        prepared_colors
    )

    # 建立色号映射
    color_map = {}
    for color in prepared_colors:
        color_map[color["code"]] = tuple(color["rgb"])

    # 生成图纸
    label_size = 36
    canvas_width = width * cell_size + label_size
    canvas_height = height * cell_size + label_size

    img = Image.new(
        "RGB",
        (canvas_width, canvas_height),
        (255, 255, 255)
    )

    pixels = img.load()

    # 绘制色块
    for y in range(height):
        for x in range(width):
            code = pattern[y][x]
            rgb = color_map[code]
            px = label_size + x * cell_size
            py = label_size + y * cell_size

            for dy in range(cell_size):
                for dx in range(cell_size):
                    if dx < cell_size and dy < cell_size:
                        pixels[px + dx, py + dy] = rgb

    # 绘制网格线
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)

    # 竖线
    for x in range(width + 1):
        px = label_size + x * cell_size
        draw.line([(px, label_size), (px, canvas_height)], fill=(180, 180, 180), width=1)

    # 横线
    for y in range(height + 1):
        py = label_size + y * cell_size
        draw.line([(label_size, py), (canvas_width, py)], fill=(180, 180, 180), width=1)

    # 边框
    draw.rectangle(
        [(label_size, label_size), (canvas_width - 1, canvas_height - 1)],
        outline=(100, 100, 100),
        width=2
    )

    # 保存为PNG
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename=pindou_pattern_{width}x{height}.png"
        }
    )


# =========================
# 新增：导出 PDF
# =========================

@app.post("/export-pdf")
async def export_pdf(

    image: UploadFile = File(...),

    width: int = Form(100),

    height: int = Form(100),

    cell_size: int = Form(4)  # PDF中每个格子的大小（mm）
):

    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm

    # 读取图片并转为拼豆图纸
    contents = await image.read()

    original_image = Image.open(
        io.BytesIO(contents)
    ).convert("RGB")

    mosaic = original_image.resize(
        (width, height),
        Image.Resampling.LANCZOS
    )

    # 颜色匹配
    pattern, statistics = match_image(
        mosaic,
        prepared_colors
    )

    # 建立色号映射
    color_map = {}
    for color in prepared_colors:
        color_map[color["code"]] = tuple(color["rgb"])

    # 创建PDF（A4横向）
    page_width, page_height = landscape(A4)
    margin = 15 * mm

    # 计算图纸尺寸
    label_size = 8 * mm
    grid_size = cell_size * mm

    total_width = width * grid_size + label_size
    total_height = height * grid_size + label_size

    # 如果图纸太大，自动缩小
    max_width = page_width - 2 * margin
    max_height = page_height - 2 * margin

    scale = 1.0
    if total_width > max_width or total_height > max_height:
        scale_x = max_width / total_width
        scale_y = max_height / total_height
        scale = min(scale_x, scale_y, 1.0)
        grid_size = grid_size * scale
        label_size = label_size * scale
        total_width = width * grid_size + label_size
        total_height = height * grid_size + label_size

    # 居中偏移
    offset_x = (page_width - total_width) / 2
    offset_y = (page_height - total_height) / 2

    # 创建PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    # 绘制标题
    c.setFont("Helvetica-Bold", 16)
    title = f"拼豆图纸  {width}×{height}  共{width * height}颗"
    c.drawCentredString(page_width / 2, page_height - 15 * mm, title)

    # 绘制网格和色块
    for y in range(height):
        for x in range(width):
            code = pattern[y][x]
            rgb = color_map[code]

            px = offset_x + label_size + x * grid_size
            py = offset_y + label_size + (height - 1 - y) * grid_size

            # 填充颜色
            c.setFillColorRGB(
                rgb[0] / 255.0,
                rgb[1] / 255.0,
                rgb[2] / 255.0
            )
            c.rect(px, py, grid_size, grid_size, fill=1, stroke=0)

    # 绘制网格线
    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.setLineWidth(0.3)

    for x in range(width + 1):
        px = offset_x + label_size + x * grid_size
        c.line(px, offset_y + label_size, px, offset_y + label_size + height * grid_size)

    for y in range(height + 1):
        py = offset_y + label_size + y * grid_size
        c.line(offset_x + label_size, py, offset_x + label_size + width * grid_size, py)

    # 绘制边框
    c.setStrokeColorRGB(0.3, 0.3, 0.3)
    c.setLineWidth(1.5)
    c.rect(
        offset_x + label_size,
        offset_y + label_size,
        width * grid_size,
        height * grid_size
    )

    # 绘制行列号
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.2, 0.2, 0.2)

    for x in range(width):
        px = offset_x + label_size + x * grid_size + grid_size / 2
        py = offset_y + label_size - 3 * mm
        c.drawCentredString(px, py, str(x + 1))

    for y in range(height):
        px = offset_x + label_size - 5 * mm
        py = offset_y + label_size + (height - 1 - y) * grid_size + grid_size / 2
        c.drawCentredString(px, py, str(y + 1))

    # 绘制颜色统计表
    stats_x = offset_x + total_width + 6 * mm
    stats_y = offset_y + total_height - 5 * mm

    if stats_x + 45 * mm < page_width - margin:
        # 标题
        c.setFont("Helvetica-Bold", 10)
        c.drawString(stats_x, stats_y, "色号统计")

        # 统计内容
        c.setFont("Helvetica", 7)
        row_height = 4.5 * mm
        max_rows = min(len(statistics), 25)

        for i in range(max_rows):
            stat = statistics[i]
            y_pos = stats_y - (i + 1) * row_height - 2 * mm

            if y_pos < 5 * mm:
                break

            # 颜色方块
            rgb = stat["rgb"]
            c.setFillColorRGB(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
            c.rect(stats_x, y_pos, 3.5 * mm, 3 * mm, fill=1, stroke=1)

            # 色号和数量
            c.setFillColorRGB(0, 0, 0)
            c.drawString(stats_x + 4.5 * mm, y_pos + 0.3 * mm, f"{stat['code']}  x{stat['count']}")

        if len(statistics) > max_rows:
            c.drawString(stats_x, stats_y - (max_rows + 1) * row_height - 2 * mm,
                        f"... 共 {len(statistics)} 种颜色")

    c.save()

    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=pindou_pattern_{width}x{height}.pdf"
        }
    )