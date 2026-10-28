import os
import re
from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright

docs_dir = r"C:\Users\ANGEL RUIZ\.gemini\antigravity\scratch\synapse-4d\docs"
md_path = os.path.join(docs_dir, "WHITE_PAPER.md")
html_path = os.path.join(docs_dir, "WHITE_PAPER.html")
pdf_path = os.path.join(docs_dir, "WHITE_PAPER.pdf")

with open(md_path, "r", encoding="utf-8") as f:
    md_content = f.read()

# Convert Markdown to HTML
md = MarkdownIt("commonmark", {"html": True}).enable("table")
body_html = md.render(md_content)

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Synapse 4D: A Multi-Dimensional Cognitive State Matrix</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"
    onload="renderMathInElement(document.body, {{delimiters: [{{left: '$$', right: '$$', display: true}}, {{left: '$', right: '$', display: false}}]}});">
</script>
<style>
  @page {{
    size: letter;
    margin: 22mm 18mm 22mm 18mm;
    @top-center {{
      content: "Synapse 4D: Multi-Dimensional Cognitive State Matrix — Defensive Prior Art Publication";
      font-size: 8pt;
      font-family: 'Times New Roman', serif;
      color: #555;
      border-bottom: 0.5pt solid #ccc;
      padding-bottom: 4px;
    }}
    @bottom-center {{
      content: "Ángel Ruiz (@MShesat) • Prior Art Specification • Page " counter(page);
      font-size: 8pt;
      font-family: 'Times New Roman', serif;
      color: #555;
      border-top: 0.5pt solid #ccc;
      padding-top: 4px;
    }}
  }}

  body {{
    font-family: 'Times New Roman', 'Liberation Serif', serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #111;
    margin: 0;
    padding: 0;
    text-align: justify;
  }}

  h1 {{
    font-size: 18pt;
    font-weight: bold;
    text-align: center;
    line-height: 1.25;
    margin-top: 0;
    margin-bottom: 12pt;
    letter-spacing: -0.3pt;
  }}

  h2 {{
    font-size: 12pt;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.4pt;
    margin-top: 20pt;
    margin-bottom: 8pt;
    border-bottom: 0.75pt solid #222;
    padding-bottom: 2pt;
    page-break-after: avoid;
  }}

  h3 {{
    font-size: 10.5pt;
    font-weight: bold;
    margin-top: 14pt;
    margin-bottom: 4pt;
    page-break-after: avoid;
  }}

  h4 {{
    font-size: 10pt;
    font-weight: bold;
    font-style: italic;
    margin-top: 10pt;
    margin-bottom: 2pt;
    page-break-after: avoid;
  }}

  p {{
    margin: 0 0 8pt 0;
    text-indent: 14pt;
  }}

  p:first-of-type, h1 + p, h2 + p, h3 + p, h4 + p, hr + p, blockquote + p {{
    text-indent: 0;
  }}

  ul, ol {{
    margin: 0 0 10pt 18pt;
    padding: 0;
  }}

  li {{
    margin-bottom: 3pt;
  }}

  blockquote {{
    margin: 10pt 16pt;
    padding: 8pt 12pt;
    background-color: #f8f9fa;
    border-left: 2.5pt solid #2c3e50;
    font-size: 9.5pt;
  }}

  pre {{
    background: #fdfdfd;
    border: 0.5pt solid #bbb;
    padding: 8pt 10pt;
    margin: 10pt 0;
    font-family: 'Courier New', monospace;
    font-size: 7.5pt;
    line-height: 1.2;
    overflow-x: auto;
    page-break-inside: avoid;
  }}

  code {{
    font-family: 'Courier New', monospace;
    font-size: 8.5pt;
    background: #f4f4f4;
    padding: 1pt 3pt;
    border-radius: 2pt;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0 16pt 0;
    font-size: 8.5pt;
    page-break-inside: avoid;
  }}

  th {{
    border-top: 1.5pt solid #222;
    border-bottom: 1pt solid #222;
    padding: 5pt 4pt;
    text-align: left;
    font-weight: bold;
  }}

  td {{
    border-bottom: 0.5pt solid #ddd;
    padding: 4pt;
  }}

  tr:last-child td {{
    border-bottom: 1.5pt solid #222;
  }}

  hr {{
    border: none;
    border-top: 0.5pt solid #ccc;
    margin: 16pt 0;
  }}

  .katex-display {{
    margin: 8pt 0 !important;
  }}
</style>
</head>
<body>
{body_html}
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"HTML written to {html_path}")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{html_path.replace(os.sep, '/')}")
    page.wait_for_timeout(3000) # Wait for KaTeX to finish rendering formulas
    page.pdf(
        path=pdf_path,
        format="Letter",
        print_background=True,
        margin={"top": "22mm", "bottom": "22mm", "left": "18mm", "right": "18mm"}
    )
    browser.close()

print(f"PDF successfully generated at {pdf_path}")
