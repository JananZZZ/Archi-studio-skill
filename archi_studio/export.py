from __future__ import annotations

from pathlib import Path
import shutil
import subprocess


def export_svg(svg_path: Path, make_png: bool = True, make_pdf: bool = True) -> dict[str, str]:
    out = {"svg": str(svg_path)}
    png = svg_path.with_suffix(".png")
    pdf = svg_path.with_suffix(".pdf")
    cairosvg = None
    try:
        import cairosvg as _cairosvg
        cairosvg = _cairosvg
    except Exception:
        pass
    if cairosvg:
        if make_png:
            cairosvg.svg2png(url=str(svg_path), write_to=str(png), output_width=1880, output_height=3760)
            out["png"] = str(png)
        if make_pdf:
            cairosvg.svg2pdf(url=str(svg_path), write_to=str(pdf))
            out["pdf"] = str(pdf)
        return out
    inkscape = shutil.which("inkscape")
    if inkscape:
        if make_png:
            subprocess.run([inkscape, str(svg_path), "--export-type=png", "--export-width=1880", "--export-height=3760", f"--export-filename={png}"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out["png"] = str(png)
        if make_pdf:
            subprocess.run([inkscape, str(svg_path), "--export-type=pdf", "--export-text-to-path", f"--export-filename={pdf}"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out["pdf"] = str(pdf)
        return out
    out["warning"] = "No CairoSVG/Inkscape renderer available; SVG exported only."
    return out


def compose_a4(project_pdf: Path, technical_pdf: Path, out_pdf: Path) -> bool:
    try:
        import fitz
    except Exception:
        return False
    A4W, A4H = 595.275590551, 841.88976378
    mm = 72/25.4
    pw, ph = 97*mm, 194*mm
    gap = 4.5*mm
    left = (A4W - (2*pw + gap))/2
    top = (A4H - ph)/2
    doc = fitz.open(); page = doc.new_page(width=A4W, height=A4H)
    for i, src_path in enumerate([project_pdf, technical_pdf]):
        src = fitz.open(str(src_path))
        x = left + i*(pw+gap)
        page.show_pdf_page(fitz.Rect(x, top, x+pw, top+ph), src, 0, keep_proportion=True)
        src.close()
    page.draw_line(fitz.Point(A4W/2, top-5), fitz.Point(A4W/2, top+ph+5), color=(0.87,0.90,0.94), width=0.4)
    doc.save(str(out_pdf), deflate=True)
    doc.close()
    return True
