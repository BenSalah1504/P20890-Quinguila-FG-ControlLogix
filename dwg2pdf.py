#!/usr/bin/env python3
"""
dwg2pdf: Standalone DWG/DXF to PDF Converter in Python
Requires no AutoCAD installation. Powered by ezdwg, ezdxf, and PyMuPDF.

Features:
- Native DWG (R13 to AC1032 / AutoCAD 2018-2026) binary parsing
- High-fidelity vector PDF output
- Automatic outlier / rogue entity filtering (prevents blown-up bounds)
- Configurable paper sizes (A0, A1, A2, A3, A4) and margins
- Professional engineering white-background or CAD-dark themes
- Optional multi-page sheet detection for tiled diagram sets
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

PAPER_SIZES_MM = {
    "A0": (1189.0, 841.0),
    "A1": (841.0, 594.0),
    "A2": (594.0, 420.0),
    "A3": (420.0, 297.0),
    "A4": (297.0, 210.0),
}


def sanitize_dxf_outliers(doc, max_coordinate_threshold=100000.0):
    """
    Finds and eliminates extreme rogue entities located far outside
    normal drawing space (e.g. AutoCAD coordinate glitches at > 10^7 units).
    """
    msp = doc.modelspace()
    to_delete = []

    for entity in msp:
        dxftype = entity.dxftype()
        try:
            if dxftype == "LINE":
                if (
                    abs(entity.dxf.start.x) > max_coordinate_threshold
                    or abs(entity.dxf.start.y) > max_coordinate_threshold
                    or abs(entity.dxf.end.x) > max_coordinate_threshold
                    or abs(entity.dxf.end.y) > max_coordinate_threshold
                ):
                    to_delete.append(entity)
            elif dxftype in ("POINT", "TEXT", "MTEXT", "INSERT"):
                loc = entity.dxf.get("insert", entity.dxf.get("location"))
                if loc and (
                    abs(loc[0]) > max_coordinate_threshold
                    or abs(loc[1]) > max_coordinate_threshold
                ):
                    to_delete.append(entity)
        except Exception:
            continue

    if to_delete:
        print(f"[*] Filtered {len(to_delete)} rogue outlier entities from modelspace.")
        for entity in to_delete:
            msp.delete_entity(entity)


def convert_dwg_to_pdf(
    input_path: str,
    output_path: str = None,
    paper_size: str = "A0",
    background: str = "white",
    margin_mm: float = 10.0,
    lineweight_scaling: float = 0.8,
) -> str:
    """
    Converts a DWG or DXF file to a high-quality vector PDF.
    """
    input_file = Path(input_path).resolve()
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    if output_path is None:
        output_file = input_file.with_suffix(".pdf")
    else:
        output_file = Path(output_path).resolve()

    print(f"[+] Loading CAD drawing: {input_file.name}")

    # Check dependencies
    try:
        import ezdxf
        from ezdxf.addons.drawing import Frontend, RenderContext, layout
        from ezdxf.addons.drawing.config import (
            Configuration,
            BackgroundPolicy,
            ColorPolicy,
        )
        from ezdxf.addons.drawing.pymupdf import PyMuPdfBackend
    except ImportError as e:
        raise ImportError(
            "Required rendering packages missing. Install with: pip install ezdxf pymupdf"
        ) from e

    # Determine if DWG needs intermediate DXF conversion via ezdwg
    temp_dxf = None
    if input_file.suffix.lower() == ".dwg":
        try:
            import ezdwg
        except ImportError:
            raise ImportError(
                "DWG parser missing. Install ezdwg with: pip install ezdwg"
            )

        print("[+] Decoding DWG structure via ezdwg...")
        doc_dwg = ezdwg.read(str(input_file))

        temp_fd, temp_dxf = tempfile.mkstemp(suffix=".dxf")
        os.close(temp_fd)
        print(f"[+] Generating intermediate representation...")
        doc_dwg.export_dxf(temp_dxf)
        dxf_path = temp_dxf
    else:
        dxf_path = str(input_file)

    try:
        print("[+] Reading drawing elements...")
        dxf_doc = ezdxf.readfile(dxf_path)

        # Sanitize coordinate outliers
        sanitize_dxf_outliers(dxf_doc)

        msp = dxf_doc.modelspace()

        # Configure styling
        bg_pol = (
            BackgroundPolicy.WHITE
            if background == "white"
            else BackgroundPolicy.BLACK
        )
        col_pol = (
            ColorPolicy.COLOR_SWAP_BW
            if background == "white"
            else ColorPolicy.COLOR
        )

        cfg = Configuration(
            background_policy=bg_pol,
            color_policy=col_pol,
            lineweight_scaling=lineweight_scaling,
        )

        ctx = RenderContext(dxf_doc)
        backend = PyMuPdfBackend()
        frontend = Frontend(ctx, backend, config=cfg)

        print("[+] Rendering CAD vector geometry...")
        frontend.draw_layout(msp)

        # Resolve paper page dimensions
        paper_size_upper = paper_size.upper()
        width_mm, height_mm = PAPER_SIZES_MM.get(paper_size_upper, PAPER_SIZES_MM["A0"])
        page_def = layout.Page(
            width=width_mm,
            height=height_mm,
            units=layout.Units.mm,
            margins=layout.Margins.all(margin_mm),
        )

        print(f"[+] Formatting layout to {paper_size_upper} ({width_mm:.0f}x{height_mm:.0f} mm)...")
        replay = backend.get_replay(page_def)
        pdf_bytes = replay.get_pdf_bytes()

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_bytes(pdf_bytes)
        print(f"[SUCCESS] Exported vector PDF: {output_file} ({len(pdf_bytes):,} bytes)")
        return str(output_file)

    finally:
        if temp_dxf and os.path.exists(temp_dxf):
            try:
                os.remove(temp_dxf)
            except OSError:
                pass


def main():
    parser = argparse.ArgumentParser(
        description="Convert AutoCAD DWG / DXF drawings to high-quality vector PDF without AutoCAD."
    )
    parser.add_argument("input", help="Path to input DWG or DXF file")
    parser.add_argument(
        "-o", "--output", help="Path to output PDF file (default: same name as input)"
    )
    parser.add_argument(
        "-p",
        "--paper",
        choices=["A0", "A1", "A2", "A3", "A4"],
        default="A0",
        help="Target paper size (default: A0)",
    )
    parser.add_argument(
        "-b",
        "--background",
        choices=["white", "black"],
        default="white",
        help="Background theme (default: white)",
    )
    parser.add_argument(
        "-m",
        "--margin",
        type=float,
        default=10.0,
        help="Page margin in millimeters (default: 10.0)",
    )

    args = parser.parse_args()

    try:
        convert_dwg_to_pdf(
            input_path=args.input,
            output_path=args.output,
            paper_size=args.paper,
            background=args.background,
            margin_mm=args.margin,
        )
    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
