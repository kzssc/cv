---
title: Sisheng Chris Zhang — Academic & Professional CV Repository
subtitle: Markdown-Based Curriculum Vitae with Strict 2-Page Constraint
author: S. Chris Zhang^[Law, Universitat Pompeu Fabra, Barcelona / academic@czhang.uk ]
lang: en-gb
abstract:
note:
---

# Academic & Professional Curriculum Vitae

This repository contains the plain-text Markdown source and automated publishing pipeline for Sisheng Chris Zhang's academic and professional Curriculum Vitae.

The system enforces a strict two-page limitation across web preview and print/PDF output.

## Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── verify-and-build.yml   # CI verification and PDF compilation pipeline
├── .githooks/
│   └── pre-commit                 # Git hook enforcing strict 2-page limit locally
├── _layouts/
│   └── cv.html                    # Layout template for HTML and GitHub Pages
├── media/
│   ├── screen.css                 # Web responsive stylesheet
│   └── print.css                  # Print stylesheet with strict A4 2-page rules
├── scripts/
│   └── build_and_verify.py        # Automated Markdown-to-HTML, PDF render, & page-count verifier
├── index.md                       # Canonical Markdown CV source
├── index.html                     # Generated HTML version
├── cv.pdf                         # Verified 2-page compiled PDF
├── Makefile                       # Convenience targets (build, verify, clean)
└── _config.yml                    # Jekyll site configuration
```

## The Strict 2-Page Restriction

Academic and fellowship applications frequently mandate hard two-page constraints. This repository enforces this limit through three defensive layers:

1. **Explicit Page Partitioning**: Content is divided across two calibrated A4 pages with a deliberate `<div class="page-break"></div>` breakpoint between major appointments.
2. **Deterministic Print Typography**: The print stylesheet (`media/print.css`) fixes font metrics, line heights, margins, and page boundaries to prevent vertical expansion.
3. **Automated Verification Engine**: The Python verification script (`scripts/build_and_verify.py`) renders the document via headless Google Chrome and queries PDF metadata. If the resulting document exceeds or undercuts two pages, the script raises an error and terminates with an exit code of `1`.

## Local Usage

### Requirements

- Python 3.8+
- [Pandoc](https://pandoc.org)
- Google Chrome or Chromium (installed in standard location or specified via `CHROME_BIN`)
- `poppler` (for `pdfinfo`)

### Building and Verifying

Run the Makefile default target:

```bash
make
```

Or execute the Python script directly:

```bash
python3 scripts/build_and_verify.py
```

### Git Pre-Commit Hook

The pre-commit hook runs the verification script automatically prior to every commit:

```bash
git config core.hooksPath .githooks
```

Any edit to `index.md` that pushes the content onto a third page will automatically abort the commit.

## GitHub Pages Deployment

The repository is fully compatible with GitHub Pages:

1. Push this repository to GitHub (e.g. `kzssc/cv`).
2. Navigate to **Settings > Pages**.
3. Under **Build and deployment**, select **Deploy from a branch** with branch `main` and folder `/ (root)`.
