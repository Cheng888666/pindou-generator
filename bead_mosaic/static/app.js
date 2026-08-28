const imageInput =
    document.getElementById("imageInput");

const selectButton =
    document.getElementById("selectButton");

const uploadArea =
    document.getElementById("uploadArea");

const fileInfo =
    document.getElementById("fileInfo");

const fileName =
    document.getElementById("fileName");

const fileSize =
    document.getElementById("fileSize");

const originalPreview =
    document.getElementById("originalPreview");

const mosaicPreview =
    document.getElementById("mosaicPreview");

const patternPreview =
    document.getElementById("patternPreview");

const generateButton =
    document.getElementById("generateButton");

const progressContainer =
    document.getElementById("progressContainer");

const progressFill =
    document.getElementById("progressFill");

const progressText =
    document.getElementById("progressText");

const resetButton =
    document.getElementById("resetButton");

const widthInput =
    document.getElementById("width");

const heightInput =
    document.getElementById("height");

const keepRatio =
    document.getElementById("keepRatio");

const colorCount =
    document.getElementById("colorCount");

const totalBeads =
    document.getElementById("totalBeads");

const colorList =
    document.getElementById("colorList");


let currentFile = null;
let currentImage = null;

let currentResult = null;
let currentPatternCanvas = null;


/* =========================
   选择图片
========================= */

selectButton.addEventListener(
    "click",
    () => {
        imageInput.click();
    }
);


imageInput.addEventListener(
    "change",
    (event) => {

        const file =
            event.target.files[0];

        if (!file) {
            return;
        }

        handleImage(file);
    }
);


/* =========================
   拖拽上传
========================= */

uploadArea.addEventListener(
    "dragover",
    (event) => {

        event.preventDefault();

        uploadArea.classList.add(
            "dragover"
        );
    }
);


uploadArea.addEventListener(
    "dragleave",
    () => {

        uploadArea.classList.remove(
            "dragover"
        );
    }
);


uploadArea.addEventListener(
    "drop",
    (event) => {

        event.preventDefault();

        uploadArea.classList.remove(
            "dragover"
        );

        const file =
            event.dataTransfer.files[0];

        if (!file) {
            return;
        }

        if (!file.type.startsWith("image/")) {

            alert(
                "请选择图片文件。"
            );

            return;
        }

        handleImage(file);
    }
);


/* =========================
   处理图片
========================= */

function handleImage(file) {

    currentFile = file;

    fileName.textContent =
        file.name;

    fileSize.textContent =
        formatFileSize(file.size);

    fileInfo.style.display =
        "block";


    const reader =
        new FileReader();


    reader.onload =
        (event) => {

            const img =
                new Image();


            img.onload =
                () => {

                    currentImage = img;

                    showOriginalImage(img);

                    updateHeight();

                };


            img.src =
                event.target.result;
        };


    reader.readAsDataURL(file);
}


/* =========================
   显示原图
========================= */

function showOriginalImage(img) {

    originalPreview.innerHTML = "";

    const image =
        document.createElement("img");

    image.src =
        img.src;

    image.className =
        "preview-image";

    originalPreview.appendChild(
        image
    );
}


/* =========================
   自动计算高度
========================= */

function updateHeight() {

    if (!currentImage) {
        return;
    }

    if (!keepRatio.checked) {
        return;
    }

    const width =
        parseInt(
            widthInput.value
        );

    if (!width) {
        return;
    }

    const ratio =
        currentImage.height /
        currentImage.width;

    const height =
        Math.max(
            1,
            Math.round(
                width * ratio
            )
        );

    heightInput.value =
        height;
}


widthInput.addEventListener(
    "input",
    updateHeight
);


keepRatio.addEventListener(
    "change",
    updateHeight
);


/* =========================
   开始生成
========================= */

generateButton.addEventListener(
    "click",
    async () => {

        if (!currentFile) {

            alert(
                "请先上传一张图片。"
            );

            return;
        }


        const width =
            parseInt(
                widthInput.value
            );

        const height =
            parseInt(
                heightInput.value
            );

        const colors =
            parseInt(
                colorCount.value
            );


        if (!width || width < 10) {

            alert(
                "请输入正确的拼豆宽度。"
            );

            return;
        }


        if (!height || height < 10) {

            alert(
                "请输入正确的拼豆高度。"
            );

            return;
        }


        await sendToPython(
            currentFile,
            width,
            height,
            colors
        );

    }
);


/* =========================
   发送给 Python
========================= */

async function sendToPython(
    file,
    width,
    height,
    colors
) {

    generateButton.disabled =
        true;

    progressContainer.style.display =
        "block";

    progressFill.style.width =
        "20%";

    progressText.textContent =
        "20%";


    const formData =
        new FormData();


    formData.append(
        "image",
        file
    );

    formData.append(
        "width",
        width
    );

    formData.append(
        "height",
        height
    );

    formData.append(
        "color_count",
        colors
    );


    try {

        progressFill.style.width =
            "40%";

        progressText.textContent =
            "40%";


        const response =
            await fetch(
                "http://127.0.0.1:8000/generate",
                {
                    method: "POST",
                    body: formData
                }
            );


        progressFill.style.width =
            "70%";

        progressText.textContent =
            "70%";


        if (!response.ok) {

            throw new Error(
                "Python服务器返回错误：" +
                response.status
            );

        }


        const result =
            await response.json();


        console.log(
            "Python返回：",
            result
        );


        progressFill.style.width =
            "100%";

        progressText.textContent =
            "100%";


        currentResult =
            result;


        showBackendResult(
            result
        );


    } catch (error) {

        console.error(error);

        alert(
            "连接 Python 后端失败。\n\n" +
            "请确认 FastAPI 服务器正在运行。\n\n" +
            error.message
        );

    } finally {

        generateButton.disabled =
            false;

    }

}


/* =========================
   显示 Python 返回结果
========================= */

function showBackendResult(result) {

    /* =========================
       显示马赛克
    ========================= */

    mosaicPreview.innerHTML = "";

    const mosaicImage =
        document.createElement("img");

    mosaicImage.src =
        result.mosaic;

    mosaicImage.className =
        "preview-image";

    mosaicPreview.appendChild(
        mosaicImage
    );


    /* =========================
       清空拼豆图纸
    ========================= */

    patternPreview.innerHTML = "";


    const canvas =
        document.createElement(
            "canvas"
        );


    canvas.id =
        "patternCanvas";


    patternPreview.appendChild(
        canvas
    );


    currentPatternCanvas =
        canvas;


    /* =========================
       绘制拼豆图纸
    ========================= */

    drawPattern(
        canvas,
        result.pattern,
        result.statistics,
        result.width,
        result.height
    );


    /* =========================
       总拼豆数量
    ========================= */

    totalBeads.textContent =
        result.total_beads.toLocaleString();


    /* =========================
       颜色统计
    ========================= */

    colorList.innerHTML = "";


    result.statistics.forEach(
        (color) => {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "color-stat-item";


            item.innerHTML = `

                <div
                    class="color-swatch"
                    style="
                        background:${color.hex};
                    "
                ></div>

                <div
                    class="color-stat-info"
                >

                    <div>
                        ${color.code}
                    </div>

                    <div
                        style="
                            font-size:11px;
                            color:#9ca3af;
                        "
                    >
                        ${color.count} 颗
                    </div>

                </div>

            `;


            colorList.appendChild(
                item
            );

        }
    );


    console.log(
        "MARD 使用颜色：",
        result.color_count
    );


    console.log(
        "拼豆总数：",
        result.total_beads
    );

}


/* =========================
   绘制拼豆图纸
========================= */

function drawPattern(
    canvas,
    pattern,
    statistics,
    width,
    height
) {

    /*
       这里仍然使用较大的实际尺寸，
       保证导出的 PNG 清晰。

       CSS 会负责把它缩小到预览区域。
    */

    const cellSize = 32;

    const labelSize = 36;


    canvas.width =
        width * cellSize +
        labelSize;

    canvas.height =
        height * cellSize +
        labelSize;


    const ctx =
        canvas.getContext("2d");


    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );


    /* =========================
       MARD 色号 → HEX
    ========================= */

    const colorMap = {};


    statistics.forEach(
        (color) => {

            colorMap[color.code] =
                color.hex;

        }
    );


    /* =========================
       绘制拼豆
    ========================= */

    for (
        let y = 0;
        y < height;
        y++
    ) {

        for (
            let x = 0;
            x < width;
            x++
        ) {

            const code =
                pattern[y][x];


            const color =
                colorMap[code] ||
                "#FFFFFF";


            const px =
                labelSize +
                x * cellSize;


            const py =
                labelSize +
                y * cellSize;


            ctx.fillStyle =
                color;


            ctx.fillRect(
                px,
                py,
                cellSize,
                cellSize
            );


            ctx.strokeStyle =
                "#999999";


            ctx.lineWidth =
                1;


            ctx.strokeRect(
                px,
                py,
                cellSize,
                cellSize
            );


            ctx.fillStyle =
                getTextColor(color);


            ctx.font =
                "bold 9px Arial";


            ctx.textAlign =
                "center";


            ctx.textBaseline =
                "middle";


            ctx.fillText(
                code,
                px +
                    cellSize / 2,
                py +
                    cellSize / 2
            );

        }

    }


    /* =========================
       行号
    ========================= */

    ctx.fillStyle =
        "#333333";


    ctx.font =
        "11px Arial";


    ctx.textAlign =
        "center";


    ctx.textBaseline =
        "middle";


    for (
        let y = 0;
        y < height;
        y++
    ) {

        ctx.fillText(

            y + 1,

            labelSize / 2,

            labelSize +
            y * cellSize +
            cellSize / 2

        );

    }


    /* =========================
       列号
    ========================= */

    for (
        let x = 0;
        x < width;
        x++
    ) {

        ctx.fillText(

            x + 1,

            labelSize +
            x * cellSize +
            cellSize / 2,

            labelSize / 2

        );

    }

}


/* =========================
   根据背景颜色决定文字颜色
========================= */

function getTextColor(hex) {

    const r =
        parseInt(
            hex.substring(1, 3),
            16
        );

    const g =
        parseInt(
            hex.substring(3, 5),
            16
        );

    const b =
        parseInt(
            hex.substring(5, 7),
            16
        );


    const brightness =
        (
            r * 299 +
            g * 587 +
            b * 114
        ) / 1000;


    return brightness > 150
        ? "#111111"
        : "#FFFFFF";
}


/* =========================
   PNG 导出
========================= */

document
    .getElementById("downloadPng")
    .addEventListener(
        "click",
        downloadPNG
    );


function downloadPNG() {

    if (!currentPatternCanvas) {

        alert(
            "请先生成拼豆图纸。"
        );

        return;
    }


    const link =
        document.createElement("a");


    link.download =
        "拼豆图纸.png";


    link.href =
        currentPatternCanvas.toDataURL(
            "image/png"
        );


    link.click();
}


/* =========================
   PDF 导出
========================= */

document
    .getElementById("downloadPdf")
    .addEventListener(
        "click",
        downloadPDF
    );


function downloadPDF() {

    if (!currentPatternCanvas) {

        alert(
            "请先生成拼豆图纸。"
        );

        return;
    }


    if (
        typeof window.jspdf ===
        "undefined"
    ) {

        alert(
            "PDF组件尚未加载，请检查网络连接后刷新页面。"
        );

        return;
    }


    const {
        jsPDF
    } = window.jspdf;


    const canvas =
        currentPatternCanvas;


    const imageData =
        canvas.toDataURL(
            "image/png"
        );


    const pdf =
        new jsPDF({
            orientation:
                canvas.width >=
                canvas.height
                    ? "landscape"
                    : "portrait",

            unit: "mm",

            format: "a4"
        });


    const pageWidth =
        pdf.internal.pageSize.getWidth();


    const pageHeight =
        pdf.internal.pageSize.getHeight();


    const margin =
        10;


    const maxWidth =
        pageWidth -
        margin * 2;


    const maxHeight =
        pageHeight -
        margin * 2;


    const ratio =
        Math.min(
            maxWidth /
                canvas.width,

            maxHeight /
                canvas.height
        );


    const drawWidth =
        canvas.width *
        ratio;


    const drawHeight =
        canvas.height *
        ratio;


    const x =
        (pageWidth -
            drawWidth) /
        2;


    const y =
        (pageHeight -
            drawHeight) /
        2;


    pdf.addImage(
        imageData,
        "PNG",
        x,
        y,
        drawWidth,
        drawHeight
    );


    pdf.save(
        "拼豆图纸.pdf"
    );
}


/* =========================
   Excel 暂时保留
========================= */

document
    .getElementById("downloadExcel")
    .addEventListener(
        "click",
        () => {

            alert(
                "Excel 清单功能将在下一步实现。"
            );

        }
    );


/* =========================
   重置
========================= */

resetButton.addEventListener(
    "click",
    resetAll
);


function resetAll() {

    currentFile = null;

    currentImage = null;

    currentResult = null;

    currentPatternCanvas = null;

    imageInput.value = "";


    fileInfo.style.display =
        "none";


    originalPreview.innerHTML = `
        <div class="empty-icon">◫</div>
        <div>等待上传图片</div>
    `;


    mosaicPreview.innerHTML = `
        <div class="empty-icon">▦</div>
        <div>等待生成</div>
    `;


    patternPreview.innerHTML = `
        <canvas id="patternCanvas"></canvas>
    `;


    colorList.innerHTML = `
        <div class="empty-statistics">
            生成图纸后显示颜色统计
        </div>
    `;


    totalBeads.textContent =
        "0";


    progressContainer.style.display =
        "none";


    progressFill.style.width =
        "0%";


    progressText.textContent =
        "0%";


    generateButton.disabled =
        false;

}


/* =========================
   文件大小
========================= */

function formatFileSize(bytes) {

    if (bytes < 1024) {

        return bytes + " B";

    }


    if (
        bytes <
        1024 * 1024
    ) {

        return (
            (
                bytes / 1024
            ).toFixed(1) +
            " KB"
        );

    }


    return (
        (
            bytes /
            1024 /
            1024
        ).toFixed(1) +
        " MB"
    );

}