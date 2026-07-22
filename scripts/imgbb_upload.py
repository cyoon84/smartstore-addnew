#!/usr/bin/env python3
"""imgbb 업로드 헬퍼 (Flickr 대체, 2026-07-21).

사용:
  python3 scripts/imgbb_upload.py <이미지_또는_폴더...> [--full] [--prefix NAME]

- API 키: ~/.config/finchmart/imgbb_key (리포 커밋 금지)
- 기본: 네이버 권장 크기로 리사이즈 후 업로드
    · 정사각형 -> 1000x1000
    · 아니면  -> height 1000 + 비례 width (예: 3:4 세로 = 750x1000)
  --full 주면 원본 해상도 그대로.
- avif/webp/png/heic 등 → RGB JPEG 로 변환(투명은 흰 배경).
- 각 파일의 imgbb URL(i.ibb.co/...) 출력. 폴더 주면 이미지 전부.
- ⚠️ 가격표·내부 소싱 이미지는 넘기지 말 것(공개 호스팅).
"""
import sys, os, io, json, base64, glob, urllib.request, urllib.parse

KEY_PATH = os.path.expanduser("~/.config/finchmart/imgbb_key")
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".avif", ".heic", ".heif", ".gif", ".bmp", ".tif", ".tiff")


def load_key():
    if not os.path.exists(KEY_PATH):
        sys.exit(f"imgbb 키 없음: {KEY_PATH} (setup 필요)")
    return open(KEY_PATH).read().strip()


def collect(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for f in sorted(os.listdir(p)):
                if f.lower().endswith(IMG_EXT):
                    files.append(os.path.join(p, f))
        elif os.path.isfile(p) and p.lower().endswith(IMG_EXT):
            files.append(p)
    return files


def _open_image(path):
    """PIL open, HEIC/HEIF는 macOS sips 로 임시 변환(아이폰 기본 포맷)."""
    from PIL import Image
    if path.lower().endswith((".heic", ".heif")):
        import subprocess, tempfile
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False).name
        subprocess.run(["sips", "-s", "format", "jpeg", path, "--out", tmp],
                       check=True, capture_output=True)
        return Image.open(tmp)
    return Image.open(path)


def to_jpeg_bytes(path, full=False):
    from PIL import Image
    im = _open_image(path)
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    if not full:
        w, h = im.size
        if w == h:
            im = im.resize((1000, 1000))
        else:
            im = im.resize((round(1000 * w / h), 1000))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=90)
    return buf.getvalue(), im.size


def upload(key, jpeg_bytes, name):
    b64 = base64.b64encode(jpeg_bytes).decode()
    data = urllib.parse.urlencode({"key": key, "image": b64, "name": name}).encode()
    with urllib.request.urlopen("https://api.imgbb.com/1/upload", data=data, timeout=180) as r:
        d = json.load(r)
    if not d.get("success"):
        raise RuntimeError(str(d)[:200])
    return d["data"]["url"]


def main():
    args = sys.argv[1:]
    full = "--full" in args
    prefix = None
    if "--prefix" in args:
        i = args.index("--prefix"); prefix = args[i + 1]; del args[i:i + 2]
    args = [a for a in args if a != "--full"]
    if not args:
        sys.exit(__doc__)
    key = load_key()
    files = collect(args)
    if not files:
        sys.exit("이미지 없음")
    for idx, f in enumerate(files, 1):
        base = os.path.splitext(os.path.basename(f))[0]
        name = f"{prefix}_{idx}" if prefix else base
        name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        try:
            jb, size = to_jpeg_bytes(f, full)
            url = upload(key, jb, name)
            print(f"{os.path.basename(f)}  [{size[0]}x{size[1]}]  ->  {url}")
        except Exception as e:
            print(f"{os.path.basename(f)}  FAIL: {e}")


if __name__ == "__main__":
    main()
