#!/usr/bin/env python3
"""
Build and verify Sisheng Chris Zhang CV.
Supports dual-language Markdown (English & Chinese), generates:
  - cv.pdf (English, strictly 2 pages)
  - cv-cn.pdf (Chinese, strictly 2 pages)
  - cv-bilingual.pdf (Combined, strictly 4 pages: 2 EN + 2 CN)
Enforces strict page restrictions both locally and in CI.
"""

import os
import shutil
import subprocess
import sys
import re

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_MD_EN = os.path.join(REPO_DIR, "index.md")
INDEX_MD_CN = os.path.join(REPO_DIR, "index-cn.md")
LAYOUT_HTML = os.path.join(REPO_DIR, "_layouts", "cv.html")
INDEX_HTML_EN = os.path.join(REPO_DIR, "index.html")
INDEX_HTML_CN = os.path.join(REPO_DIR, "index-cn.html")
OUTPUT_PDF_EN = os.path.join(REPO_DIR, "cv.pdf")
OUTPUT_PDF_CN = os.path.join(REPO_DIR, "cv-cn.pdf")
OUTPUT_PDF_BILINGUAL = os.path.join(REPO_DIR, "cv-bilingual.pdf")

def find_chrome():
    candidates = [
        os.environ.get("CHROME_BIN"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None

def build_single_html(md_path, html_path):
    print(f"      Converting {os.path.basename(md_path)} -> {os.path.basename(html_path)}...")
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Separate YAML frontmatter
    body_md = md_content
    title = "Sisheng Chris Zhang — Curriculum Vitae"
    name = "Sisheng Chris ZHANG"
    cv_title = "//Curriculum Vitae"
    cv_date = "Oct 2026"
    lang = "en-gb"
    theme_color = "blue"
    photo = None

    if md_content.startswith("---"):
        parts = md_content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body_md = parts[2]
            for line in frontmatter.splitlines():
                if line.startswith("title:"):
                    title = line.split(":", 1)[1].strip().strip('"\'')
                elif line.startswith("name:"):
                    name = line.split(":", 1)[1].strip().strip('"\'')
                elif line.startswith("display_name:"):
                    name = line.split(":", 1)[1].strip().strip('"\'')
                elif line.startswith("cv_title:"):
                    cv_title = line.split(":", 1)[1].strip().strip('"\'')
                elif line.startswith("cv_date:"):
                    cv_date = line.split(":", 1)[1].strip().strip('"\'')
                elif line.startswith("lang:"):
                    lang = line.split(":", 1)[1].strip().strip('"\'')
                elif line.startswith("theme_color:"):
                    theme_color = line.split(":", 1)[1].strip().strip('"\'')
                elif line.startswith("photo:"):
                    photo = line.split(":", 1)[1].strip().strip('"\'')

    # Convert Markdown via pandoc
    pandoc_bin = shutil.which("pandoc")
    if pandoc_bin:
        cmd = [pandoc_bin, "-f", "gfm", "-t", "html"]
        res = subprocess.run(cmd, input=body_md, text=True, capture_output=True)
        if res.returncode != 0:
            print(f"Error compiling markdown with pandoc: {res.stderr}", file=sys.stderr)
            sys.exit(1)
        html_content = res.stdout
    else:
        import markdown
        html_content = markdown.markdown(body_md, extensions=['extra', 'tables'])

    # Read layout template
    with open(LAYOUT_HTML, "r", encoding="utf-8") as f:
        layout = f.read()

    # Split on page-break marker
    if "<hr" in html_content:
        pages = re.split(r"<hr\s*/?>", html_content, maxsplit=1)
    elif '<div class="page-break"></div>' in html_content:
        pages = html_content.split('<div class="page-break"></div>', 1)
    else:
        pages = [html_content, ""]

    part1 = pages[0]
    part2 = pages[1] if len(pages) > 1 else ""

    final_html = layout.replace("{{ cv_pages[0] }}", part1)
    final_html = final_html.replace("{{ cv_pages[1] }}", part2)
    final_html = re.sub(r"\{\{\s*page\.title[^\}]*\}\}", title, final_html)
    final_html = re.sub(r"\{\{\s*page\.(name|display_name)[^\}]*\}\}", name, final_html)
    final_html = re.sub(r"\{\{\s*page\.cv_title[^\}]*\}\}", cv_title, final_html)
    final_html = re.sub(r"\{\{\s*page\.cv_date[^\}]*\}\}", cv_date, final_html)
    final_html = re.sub(r"\{\{\s*page\.lang[^\}]*\}\}", lang, final_html)
    final_html = re.sub(r"\{\{\s*page\.theme_color[^\}]*\}\}", theme_color, final_html)
    final_html = re.sub(r"\{\{\s*page\.photo[^\}]*\}\}", photo or "", final_html)
    
    # Process Liquid conditions for photo
    if photo:
        final_html = re.sub(r"\{%\s*if\s+page\.photo\s*%\}(.*?)\{%\s*endif\s*%\}", r"\1", final_html, flags=re.DOTALL)
    else:
        final_html = re.sub(r"\{%\s*if\s+page\.photo\s*%\}(.*?)\{%\s*endif\s*%\}", "", final_html, flags=re.DOTALL)
    
    # Process Liquid conditions for lang
    if lang == "zh-cn":
        # Keep Chinese branch, discard English branch
        final_html = re.sub(r"\{%\s*if\s+page\.lang\s*==\s*'zh-cn'\s*%\}(.*?)\{%\s*else\s*%\}(.*?)\{%\s*endif\s*%\}", r"\1", final_html, flags=re.DOTALL)
        final_html = re.sub(r"\{%\s*if\s+page\.lang\s*!=\s*'zh-cn'\s*%\}(.*?)\{%\s*endif\s*%\}", "", final_html, flags=re.DOTALL)
        final_html = re.sub(r"\{%\s*if\s+page\.lang\s*==\s*'zh-cn'\s*%\}(.*?)\{%\s*endif\s*%\}", r"\1", final_html, flags=re.DOTALL)
    else:
        # Keep English branch, discard Chinese branch
        final_html = re.sub(r"\{%\s*if\s+page\.lang\s*==\s*'zh-cn'\s*%\}(.*?)\{%\s*else\s*%\}(.*?)\{%\s*endif\s*%\}", r"\2", final_html, flags=re.DOTALL)
        final_html = re.sub(r"\{%\s*if\s+page\.lang\s*!=\s*'zh-cn'\s*%\}(.*?)\{%\s*endif\s*%\}", r"\1", final_html, flags=re.DOTALL)
        final_html = re.sub(r"\{%\s*if\s+page\.lang\s*==\s*'zh-cn'\s*%\}(.*?)\{%\s*endif\s*%\}", "", final_html, flags=re.DOTALL)

    # Remove remaining liquid blocks
    final_html = re.sub(r"\{%.*?%\}", "", final_html)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"      Saved {html_path}")

def build_all_html():
    print("[1/4] Converting Markdown source files to HTML...")
    build_single_html(INDEX_MD_EN, INDEX_HTML_EN)
    if os.path.exists(INDEX_MD_CN):
        build_single_html(INDEX_MD_CN, INDEX_HTML_CN)

def generate_pdf_from_html(chrome, html_path, pdf_path):
    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if not os.path.exists(pdf_path):
        print(f"Error generating PDF from {html_path}: {res.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"      Saved {pdf_path}")

def generate_all_pdfs():
    print("[2/4] Generating individual PDFs using Headless Chrome...")
    chrome = find_chrome()
    if not chrome:
        print("Error: Could not locate Google Chrome or Chromium executable.", file=sys.stderr)
        print("Please install Google Chrome or set CHROME_BIN environment variable.", file=sys.stderr)
        sys.exit(1)

    generate_pdf_from_html(chrome, INDEX_HTML_EN, OUTPUT_PDF_EN)
    if os.path.exists(INDEX_HTML_CN):
        generate_pdf_from_html(chrome, INDEX_HTML_CN, OUTPUT_PDF_CN)

def combine_pdfs():
    print("[3/4] Generating combined bilingual PDF (cv-bilingual.pdf)...")
    if not os.path.exists(OUTPUT_PDF_EN) or not os.path.exists(OUTPUT_PDF_CN):
        print("Error: Both English and Chinese PDFs must exist to create bilingual PDF.", file=sys.stderr)
        sys.exit(1)

    pdfunite = shutil.which("pdfunite")
    if pdfunite:
        cmd = [pdfunite, OUTPUT_PDF_EN, OUTPUT_PDF_CN, OUTPUT_PDF_BILINGUAL]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"pdfunite failed: {res.stderr}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            from pypdf import PdfWriter
            merger = PdfWriter()
            merger.append(OUTPUT_PDF_EN)
            merger.append(OUTPUT_PDF_CN)
            merger.write(OUTPUT_PDF_BILINGUAL)
            merger.close()
        except ImportError:
            print("Error: Neither pdfunite nor pypdf available to merge PDFs.", file=sys.stderr)
            sys.exit(1)
            
    print(f"      Saved {OUTPUT_PDF_BILINGUAL}")

def get_pdf_page_count(pdf_path):
    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo:
        res = subprocess.run([pdfinfo, pdf_path], capture_output=True, text=True)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if line.startswith("Pages:"):
                    return int(line.split(":", 1)[1].strip())

    with open(pdf_path, "rb") as f:
        data = f.read()
    matches = re.findall(rb"/Type\s*/Page[^s]", data)
    if matches:
        return len(matches)

    matches_count = re.findall(rb"/Count\s+(\d+)", data)
    if matches_count:
        return int(matches_count[-1])

    return None

def verify_all_page_counts():
    print("[4/4] Verifying strict page restrictions...")
    targets = [
        (OUTPUT_PDF_EN, 2, "English CV (cv.pdf)"),
        (OUTPUT_PDF_CN, 2, "Chinese CV (cv-cn.pdf)"),
        (OUTPUT_PDF_BILINGUAL, 4, "Bilingual Combined CV (cv-bilingual.pdf)")
    ]

    has_violation = False
    for path, expected, label in targets:
        if not os.path.exists(path):
            print(f"❌ Missing expected PDF: {path}", file=sys.stderr)
            has_violation = True
            continue
        pages = get_pdf_page_count(path)
        print(f"      {label}: {pages} pages (required: {expected})")
        if pages != expected:
            print(f"      ❌ VIOLATION: Expected {expected} pages, got {pages} pages!", file=sys.stderr)
            has_violation = True

    if has_violation:
        print("\n❌ Build failed: Page count restriction violated!", file=sys.stderr)
        sys.exit(1)
    else:
        print("\n✅ SUCCESS: All documents strictly conform to their page requirements.")

if __name__ == "__main__":
    build_all_html()
    generate_all_pdfs()
    combine_pdfs()
    verify_all_page_counts()
