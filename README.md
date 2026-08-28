拼豆图纸生成器

上传照片，自动生成拼豆图纸，支持下载 PNG 和 PDF。

功能

上传图片（支持 JPG、PNG、WEBP）
设置拼豆尺寸（宽 x 高）
自动匹配 MARD 221 色卡
显示颜色统计（每种颜色需要多少颗）
下载 PNG 图纸
下载 PDF 图纸（适合打印）

技术

- Python + FastAPI（后端）
- scikit-image（颜色匹配）
- HTML + CSS + JS（前端）
- MARD 221 色卡

项目结构

bead_mosaic/
├── main.py
├── color_matcher.py
├── mard_221.json
├── requirements.txt
└── static/
    ├── index.html
    ├── style.css
    └── app.js

致谢

本工具使用 MARD 221 拼豆色卡。

作者

Cheng888666
