#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
media2html.py —— 媒体文件批量转独立 HTML

支持格式：
  图片: jpg jpeg png gif webp bmp svg ico tif tiff avif
  视频: mp4 m4v webm ogv mov mkv avi
  音频: mp3 wav ogg oga flac m4a aac opus weba

用法：
  python media2html.py 图片.jpg
  python media2html.py 某个文件夹
  python media2html.py 文件夹1 视频.mp4 音乐.mp3

输出：
  在当前目录生成 media_html_时间戳 文件夹，
  每个文件对应一个同名 .html，双击即可查看 / 播放 / 下载。
"""

import base64
import html
import json
import mimetypes
import os
import subprocess
import sys
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# 类型表
# ---------------------------------------------------------------------------

MIME_MAP = {
    # 图片
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".jpe": "image/jpeg",
    ".jfif": "image/jpeg", ".pjpeg": "image/jpeg", ".pjp": "image/jpeg",
    ".png": "image/png", ".apng": "image/apng",
    ".gif": "image/gif", ".webp": "image/webp",
    ".bmp": "image/bmp", ".svg": "image/svg+xml",
    ".ico": "image/x-icon", ".tif": "image/tiff", ".tiff": "image/tiff",
    ".avif": "image/avif", ".jxl": "image/jxl",
    # 视频
    ".mp4": "video/mp4", ".m4v": "video/mp4",
    ".webm": "video/webm", ".ogv": "video/ogg",
    ".mov": "video/quicktime", ".mkv": "video/x-matroska",
    ".avi": "video/x-msvideo",
    # 音频
    ".mp3": "audio/mpeg", ".wav": "audio/wav",
    ".ogg": "audio/ogg", ".oga": "audio/ogg",
    ".flac": "audio/flac", ".m4a": "audio/mp4",
    ".aac": "audio/aac", ".opus": "audio/opus", ".weba": "audio/webm",
}

# 浏览器基本能直接播放的视频容器（其它容器可能黑屏）
BROWSER_FRIENDLY_VIDEO = {".mp4", ".m4v", ".webm", ".ogv"}


def guess_mime(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in MIME_MAP:
        return MIME_MAP[ext]
    mime, _ = mimetypes.guess_type(str(path))
    if mime:
        return mime
    raise ValueError(f"未知类型：{path.suffix}")


def classify(mime: str) -> str:
    if mime.startswith("image/"):
        return "image"
    if mime.startswith("video/"):
        return "video"
    if mime.startswith("audio/"):
        return "audio"
    raise ValueError(f"不支持的媒体类型：{mime}")


def human_size(n: int) -> str:
    x = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if x < 1024 or unit == "GB":
            if unit == "B":
                return f"{int(x)} B"
            return f"{x:.1f} {unit}"
        x /= 1024
    return f"{x:.1f} TB"


# ---------------------------------------------------------------------------
# HTML 生成
# ---------------------------------------------------------------------------

def build_html(src: Path, mime: str, kind: str) -> str:
    data = src.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")

    name = src.name
    name_js = json.dumps(name, ensure_ascii=False)
    mime_js = json.dumps(mime)

    if kind == "image":
        content = f'<img id="media" src="data:{mime};base64,{b64}" alt="">'
        script = ""
    elif kind == "video":
        content = '<video id="media" controls playsinline preload="metadata"></video>'
        script = f"""
  // 视频用 Blob URL：data URI 不支持 Range 请求，直接放 <video src> 会播不了
  var B64 = "{b64}";
  var MIME = {mime_js};
  var bin = atob(B64);
  var bytes = new Uint8Array(bin.length);
  for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  document.getElementById("media").src =
    URL.createObjectURL(new Blob([bytes], {{ type: MIME }}));
"""
    else:  # audio
        content = '<audio id="media" controls preload="metadata"></audio>'
        script = f"""
  var B64 = "{b64}";
  var MIME = {mime_js};
  var bin = atob(B64);
  var bytes = new Uint8Array(bin.length);
  for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  document.getElementById("media").src =
    URL.createObjectURL(new Blob([bytes], {{ type: MIME }}));
"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="light dark">
<title>{html.escape(name)}</title>
<style>
  /* 默认（无系统偏好 / 不支持时）就是浅色 */
  :root {{
    --bg: #f5f5f5;
    --fg: #222;
    --media-bg: #fff;
    --media-shadow: 0 2px 14px rgba(0, 0, 0, .15);
    --bar-bg: #fff;
    --bar-border: #e2e2e2;
    --btn-bg: #f7f7f7;
    --btn-fg: #222;
    --btn-border: #d0d0d0;
    --btn-hover: #ededed;
    --btn-active: #e2e2e2;
    --meta: #777;
  }}

  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #111;
      --fg: #ddd;
      --media-bg: #1a1a1a;
      --media-shadow: 0 2px 14px rgba(0, 0, 0, .6);
      --bar-bg: #1c1c1c;
      --bar-border: #333;
      --btn-bg: #2c2c2c;
      --btn-fg: #eee;
      --btn-border: #444;
      --btn-hover: #3a3a3a;
      --btn-active: #454545;
      --meta: #888;
    }}
  }}

  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; height: 100%; }}
  body {{
    display: flex;
    flex-direction: column;
    background: var(--bg);
    color: var(--fg);
    font-family: system-ui, -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
    /* 让原生控件（滚动条等）跟随主题 */
    color-scheme: light dark;
  }}

  #viewer {{
    flex: 1 1 auto;
    min-height: 0;             /* 关键：让 flex 子项能正确收缩 */
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 12px;
    overflow: hidden;
  }}
  #viewer img,
  #viewer video {{
    max-width: 100%;
    max-height: 100%;
    display: block;
    object-fit: contain;
    background: var(--media-bg);
    box-shadow: var(--media-shadow);
  }}
  #viewer audio {{
    width: min(640px, 100%);
  }}

  #bar {{
    flex: 0 0 auto;            /* 工具栏固定高度，绝不覆盖媒体 */
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 10px 14px;
    background: var(--bar-bg);
    border-top: 1px solid var(--bar-border);
  }}
  .btn {{
    appearance: none;
    font: inherit;
    font-size: 14px;
    padding: 9px 22px;
    border: 1px solid var(--btn-border);
    border-radius: 8px;
    background: var(--btn-bg);
    color: var(--btn-fg);
    cursor: pointer;
    transition: background .15s, border-color .15s;
  }}
  .btn:hover {{ background: var(--btn-hover); }}
  .btn:active {{ background: var(--btn-active); }}

  .meta {{
    font-size: 12px;
    color: var(--meta);
    max-width: 60vw;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}
</style>
</head>
<body>

<div id="viewer">
  {content}
</div>

<div id="bar">
  <button class="btn" id="dl" type="button">下载</button>
  <span class="meta">{html.escape(name)} · {human_size(len(data))}</span>
</div>

<script>
(function () {{
  var FILENAME = {name_js};
{script}
  document.getElementById("dl").addEventListener("click", function () {{
    var m = document.getElementById("media");
    var url = m.currentSrc || m.src;
    var a = document.createElement("a");
    a.href = url;
    a.download = FILENAME;
    document.body.appendChild(a);
    a.click();
    a.remove();
  }});
}})();
</script>

</body>
</html>
"""

def convert(src: Path, out: Path) -> None:
    mime = guess_mime(src)
    kind = classify(mime)
    out.write_text(build_html(src, mime, kind), encoding="utf-8")


# ---------------------------------------------------------------------------
# 批量 / 输入 / 输出
# ---------------------------------------------------------------------------

def collect_files(paths):
    """把文件与文件夹展开成媒体文件列表。"""
    files = []
    for raw in paths:
        p = Path(raw).expanduser()
        if not p.exists():
            print(f"  ! 路径不存在：{p}")
            continue
        if p.is_dir():
            found = 0
            for f in sorted(p.rglob("*")):
                if f.is_file() and f.suffix.lower() in MIME_MAP:
                    files.append(f)
                    found += 1
            print(f"  文件夹 {p} → 找到 {found} 个媒体文件")
        elif p.is_file():
            if p.suffix.lower() in MIME_MAP:
                files.append(p)
            else:
                print(f"  ! 不支持的扩展名：{p.name}")
        else:
            print(f"  ! 跳过：{p}")
    return files


def open_folder(path: Path) -> None:
    """尽量用系统文件管理器打开目录。"""
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception:
        pass


def ask_paths():
    """无参数运行时，提示用户输入路径。"""
    print("=" * 60)
    print("媒体文件批量转 HTML")
    print("=" * 60)
    print("可以把文件 / 文件夹直接拖到终端窗口，或者手动输入。")
    print("多个路径用英文分号 ; 分隔。")
    print()
    raw = input("请输入路径：").strip()
    if not raw:
        return []
    parts = [p.strip().strip('"').strip("'") for p in raw.split(";")]
    return [p for p in parts if p]


def main() -> None:
    args = sys.argv[1:]
    if not args:
        args = ask_paths()
        print()

    if not args:
        print("没有输入，已退出。")
        return

    print("扫描输入 ...")
    files = collect_files(args)

    if not files:
        print()
        print("没有找到可转换的媒体文件。")
        return

    # 输出目录：当前工作目录下的新文件夹
    out_dir = Path.cwd() / f"media_html_{time.strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print()
    print(f"共 {len(files)} 个文件待转换")
    print(f"输出目录：{out_dir}")
    print("-" * 60)

    ok = fail = 0
    used = set()

    for i, f in enumerate(files, 1):
        try:
            # 生成输出文件名：保留原扩展名，例如 photo.jpg → photo.jpg.html
            base = f.name                      # 含原扩展名
            out = out_dir / f"{base}.html"
            n = 1
            while out.name in used or out.exists():
                out = out_dir / f"{base}_{n}.html"
                n += 1
            used.add(out.name)

            src_mb = f.stat().st_size / 1024 / 1024
            convert(f, out)
            out_mb = out.stat().st_size / 1024 / 1024

            tips = ""
            if src_mb > 200:
                tips = "  ⚠ 大文件，HTML 会非常大"
            elif f.suffix.lower() in MIME_MAP and \
                    MIME_MAP[f.suffix.lower()].startswith("video/") and \
                    f.suffix.lower() not in BROWSER_FRIENDLY_VIDEO:
                tips = "  ⚠ 该容器浏览器可能无法播放"

            print(f"[{i}/{len(files)}] {f.name} → {out.name}"
                  f"  ({src_mb:.1f} MB → {out_mb:.1f} MB){tips}")
            ok += 1
        except Exception as e:
            print(f"[{i}/{len(files)}] 失败：{f.name}  ({e})")
            fail += 1

    print()
    print("=" * 60)
    print(f"转换完成：成功 {ok}，失败 {fail}")
    print("=" * 60)
    print()
    print("输出位置：")
    print(f"  {out_dir}")
    print()
    print("每个 .html 双击即可打开，独立显示 / 播放 / 下载，无需原文件。")
    print()

    open_folder(out_dir)


if __name__ == "__main__":
    main()