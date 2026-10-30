#!/usr/bin/env python3
"""
Build and verify Sisheng Chris Zhang CV.
Enforces a strict 2-page restriction both locally and in CI.
"""

import os
import shutil
import subprocess
import sys
import re

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_MD = os.path.join(REPO_DIR, "index.md")
LAYOUT_HTML = os.path.join(REPO_DIR, "_layouts", "cv.html")
INDEX_HTML = os.path.join(REPO_DIR, "index.html")
OUTPUT_PDF = os.path.join(REPO_DIR, "cv.pdf")

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

def build_html():
    print("[1/3] Converting index.md to HTML...")
    with open(INDEX_MD, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Separate YAML frontmatter
    body_md = md_content
    title = "Sisheng Chris Zhang — Curriculum Vitae"
    name = "Sisheng Chris ZHANG"
    cv_title = "//Curriculum Vitae"
    cv_date = "Oct 2026"

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
    # Remove remaining liquid blocks
    final_html = re.sub(r"\{%.*?%\}", "", final_html)

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"      Saved {INDEX_HTML}")

def generate_pdf():
    print("[2/3] Generating PDF using Headless Chrome...")
    chrome = find_chrome()
    if not chrome:
        print("Error: Could not locate Google Chrome or Chromium executable.", file=sys.stderr)
        print("Please install Google Chrome or set CHROME_BIN environment variable.", file=sys.stderr)
        sys.exit(1)

    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={OUTPUT_PDF}",
        INDEX_HTML
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if not os.path.exists(OUTPUT_PDF):
        print(f"Error generating PDF: {res.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"      Saved {OUTPUT_PDF}")

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

def verify_page_count():
    print("[3/3] Verifying strict 2-page restriction...")
    pages = get_pdf_page_count(OUTPUT_PDF)

    if pages is None:
        print("Error: Could not determine page count from PDF metadata.", file=sys.stderr)
        sys.exit(1)

    print(f"      Document page count: {pages}")
    if pages != 2:
        print(f"\n❌ VIOLATION: Strict 2-page restriction violated!", file=sys.stderr)
        print(f"   Generated document has {pages} pages, but exactly 2 pages are required.", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\n✅ SUCCESS: Document strictly conforms to the 2-page requirement.")

if __name__ == "__main__":
    build_html()
    generate_pdf()
    verify_page_count()
