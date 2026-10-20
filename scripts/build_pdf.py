#!/usr/bin/env python3
"""Build docs/REPORT.pdf and docs/EXECUTIVE_BRIEF.pdf from the markdown files (pandoc -> HTML -> headless Chromium).
Requires pandoc and Playwright with Chromium.  Appendices are printed on landscape pages."""
import os, re, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")


def to_html(md_text, out_html, title, brief=False):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, dir=DOCS) as t:
        t.write(md_text); tmp = t.name
    try:
        subprocess.run(["pandoc", tmp, "-f", "gfm+fenced_divs", "-t", "html5", "-s", "--embed-resources", "--css", os.path.join(DOCS, "pdf.css"),
                        "--metadata", f"title={title}", "--metadata", "pagetitle=" + title, "-V", "document-css=false",
                        "--resource-path", DOCS, "-o", out_html], check=True)
    finally:
        os.unlink(tmp)
    if brief:
        h = open(out_html, encoding="utf-8").read().replace("<body", '<body class="brief"', 1)
        open(out_html, "w", encoding="utf-8").write(h)


def html_to_pdf(html, pdf):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto("file://" + html)
        pg.pdf(path=pdf, prefer_css_page_size=True, print_background=True, display_header_footer=True,
               header_template="<span></span>",
               footer_template='<div style="font-size:7px;width:100%;text-align:center;color:#666">dune-rover: research, not engineering approval. Simulation results are model-assumption dependent. Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
               margin={"top": "16mm", "bottom": "16mm", "left": "15mm", "right": "15mm"})
        b.close()


def compress(pdf):
    """Recompress streams with qpdf when it is installed (keeps the report under the 3 MB hygiene limit); skipped otherwise."""
    import shutil
    if shutil.which("qpdf"):
        tmp = pdf + ".tmp"
        subprocess.run(["qpdf", "--object-streams=generate", "--compress-streams=y", "--recompress-flate", "--compression-level=9", pdf, tmp], check=True)
        os.replace(tmp, pdf)


def main():
    rep = open(os.path.join(DOCS, "REPORT.md"), encoding="utf-8").read()
    rep = rep.replace("](../results/", "](../results/")
    i = rep.index("## Appendix A")
    rep = rep[:i] + "::: wide\n\n" + rep[i:] + "\n\n:::\n"
    # first line is the H1 title; pandoc title metadata duplicates it, so suppress by using a short title
    for name, text, brief in (("REPORT", rep, False), ("EXECUTIVE_BRIEF", open(os.path.join(DOCS, "EXECUTIVE_BRIEF.md"), encoding="utf-8").read(), True)):
        html = os.path.join(tempfile.gettempdir(), f"{name}.html")
        to_html(text, html, "dune-rover " + name.lower().replace("_", " "), brief)
        html_to_pdf(html, os.path.join(DOCS, f"{name}.pdf"))
        compress(os.path.join(DOCS, f"{name}.pdf"))
        print("wrote", os.path.join(DOCS, f"{name}.pdf"))


if __name__ == "__main__":
    main()
