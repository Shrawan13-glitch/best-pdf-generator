#!/usr/bin/env python3
"""
The Best Possible PDF in the World
Generated WITHOUT any PDF library or tool - raw PDF bytecode by hand.
This demonstrates the PDF file format specification directly.
"""

import struct
import zlib
import math
import os


class RawPDF:
    """
    Hand-crafted PDF generator using raw PDF specification.
    No external PDF libraries used - just raw bytes written to a file.
    """

    def __init__(self, filename):
        self.filename = filename
        self.objects = []  # List of (offset, content) tuples
        self.object_offsets = {}
        self.pages = []
        self.fonts = []
        self.images = []
        self.current_obj = 1
        self.page_tree_id = None
        self.catalog_id = None
        self.info_id = None

    def _new_obj(self):
        obj_id = self.current_obj
        self.current_obj += 1
        return obj_id

    def _add_obj(self, content):
        obj_id = self._new_obj()
        self.objects.append((obj_id, content))
        self.object_offsets[obj_id] = None  # Will be set during write
        return obj_id

    def _add_stream_obj(self, dictionary, stream_data):
        """Add an object with a stream (compressed)."""
        obj_id = self._new_obj()
        compressed = zlib.compress(stream_data.encode('latin-1'))
        full_content = (f"{dictionary}/Filter /FlateDecode /Length {len(compressed)}"
                        f" /DL {len(stream_data)}\nstream\n").encode('latin-1') + compressed + b"\nendstream"
        self.objects.append((obj_id, full_content))
        self.object_offsets[obj_id] = None
        return obj_id

    def _rgb(self, r, g, b):
        """Convert 0-255 RGB to 0-1 range for PDF."""
        return (r / 255.0, g / 255.0, b / 255.0)

    def _color_cmd(self, r, g, b, stroke=True):
        """Generate color command."""
        r1, g1, b1 = self._rgb(r, g, b)
        if stroke:
            return f"{r1:.3f} {g1:.3f} {b1:.3f} RG\n"
        else:
            return f"{r1:.3f} {g1:.3f} {b1:.3f} rg\n"

    def _add_page_with_content(self, width, height, content_stream, font_refs=None):
        """Add a page with the given content stream."""
        # Content stream first
        content_id = self._new_obj()
        compressed = zlib.compress(content_stream.encode('latin-1'))
        content_dict = (f"<< /Length {len(compressed)} /Filter /FlateDecode /DL {len(stream_data)} >>"
                        if False else  # placeholder
                        f"<< /Length {len(compressed)} /Filter /FlateDecode >>")
        content_obj = (f"{content_dict}\nstream\n").encode('latin-1') + compressed + b"\nendstream"
        self.objects.append((content_id, content_obj))
        self.object_offsets[content_id] = None

        # Page object
        page_id = self._new_obj()
        resources = ""
        if font_refs:
            font_refs_str = " ".join(f"{f} 0 R" for f in font_refs)
            resources = f" /Resources << /Font << {font_refs_str} >> >>"
        page_dict = f"<< /Type /Page /Parent {self.page_tree_id} 0 R /MediaBox [0 0 {width} {height}] /Contents {content_id} 0 R{resources} >>"
        self.objects.append((page_id, page_dict.encode('latin-1')))
        self.object_offsets[page_id] = None

        self.pages.append(page_id)
        return page_id

    def write(self):
        """Write the PDF file."""
        with open(self.filename, 'wb') as f:
            # Header
            f.write(b"%PDF-1.4\n")
            f.write(b"%\xe2\xe3\xcf\xd3\n")  # Binary marker

            # Write objects and track offsets
            xref_offsets = {}
            for obj_id, content in self.objects:
                xref_offsets[obj_id] = f.tell()
                f.write(f"{obj_id} 0 obj\n".encode('latin-1'))
                if isinstance(content, str):
                    f.write(content.encode('latin-1'))
                else:
                    f.write(content)
                f.write(b"\nendobj\n\n")

            # Cross-reference table
            xref_start = f.tell()
            f.write(b"xref\n")
            f.write(f"0 {self.current_obj}\n".encode('latin-1'))
            f.write(b"0000000000 65535 f \n")
            for i in range(1, self.current_obj):
                offset = xref_offsets.get(i, 0)
                f.write(f"{offset:010d} 00000 n \n".encode('latin-1'))

            # Trailer
            root_str = f"/Root {self.catalog_id} 0 R" if self.catalog_id else ""
            info_str = f"/Info {self.info_id} 0 R" if self.info_id else ""
            f.write(f"trailer\n<< /Size {self.current_obj} {root_str} {info_str} >>\n".encode('latin-1'))
            f.write(b"startxref\n")
            f.write(f"{xref_start}\n".encode('latin-1'))
            f.write(b"%%EOF\n")

        return self.filename


def dec_to_rgb(r, g, b):
    """Helper to convert decimal RGB to PDF color string."""
    return f"{r/255:.3f} {g/255:.3f} {b/255:.3f}"


def create_best_pdf():
    """Create the best PDF in the world using raw PDF bytecode."""

    pdf = RawPDF('/best_pdf_in_the_world.pdf')

    # === Object 1: Catalog ===
    pdf.catalog_id = pdf._new_obj()
    catalog = f"<< /Type /Catalog /Pages {pdf.current_obj + 1} 0 R >>"
    pdf.objects.append((pdf.catalog_id, catalog.encode('latin-1')))

    # === Object 2: Page Tree (placeholder, updated later) ===
    pdf.page_tree_id = pdf._new_obj()
    page_tree = "<< /Type /Pages /Kids [REPLACE] /Count 1 >>"
    pdf.objects.append((pdf.page_tree_id, page_tree.encode('latin-1')))

    # === Object 3: Info ===
    pdf.info_id = pdf._new_obj()
    info = (
        "<< /Title (The Best PDF in the World)"
        " /Author (Kino AI Agent)"
        " /Subject (A Visual Masterpiece)"
        " /Creator (Raw PDF Generator - No PDF Tools Used!)"
        " /Producer (Hand-crafted PDF 1.4)"
        " /CreationDate (D:20260618120000) >>"
    )
    pdf.objects.append((pdf.info_id, info.encode('latin-1')))

    # === Fonts ===
    font1_id = pdf._new_obj()  # Helvetica
    pdf.objects.append((font1_id, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>".encode('latin-1')))

    font2_id = pdf._new_obj()  # Helvetica-Bold
    pdf.objects.append((font2_id, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>".encode('latin-1')))

    font3_id = pdf._new_obj()  # Courier
    pdf.objects.append((font3_id, "<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>".encode('latin-1')))

    font4_id = pdf._new_obj()  # Times-Roman
    pdf.objects.append((font4_id, "<< /Type /Font /Subtype /Type1 /BaseFont /Times-Roman >>".encode('latin-1')))

    font_refs = [font1_id, font2_id, font3_id, font4_id]

    # ============================================================
    # PAGE 1: COVER PAGE
    # ============================================================
    cover_content = ""

    # Background gradient (layered rectangles)
    for i in range(100):
        ratio = i / 100.0
        r = int(15 + ratio * 60)
        g = int(15 + ratio * 0)
        b = int(45 + ratio * 85)
        cover_content += pdf._color_cmd(r, g, b, stroke=False)
        cover_content += f"0 {i * 8.4:.1f} 595.28 8.5 re f\n"

    # Decorative filled rectangles as "circles"
    cover_content += pdf._color_cmd(255, 255, 255, stroke=False)
    cover_content += "-30 -30 150 150 re f\n"

    cover_content += pdf._color_cmd(255, 215, 0, stroke=False)
    cover_content += "480 700 130 130 re f\n"

    cover_content += pdf._color_cmd(255, 127, 80, stroke=False)
    cover_content += "500 30 80 80 re f\n"

    cover_content += pdf._color_cmd(0, 128, 128, stroke=False)
    cover_content += "-10 740 100 100 re f\n"

    # Small decorative dots
    for pos in [(80, 250), (520, 400), (50, 550), (530, 250), (280, 100)]:
        cover_content += pdf._color_cmd(255, 255, 255, stroke=False)
        cover_content += f"{pos[0]} {pos[1]} 15 15 re f\n"

    # Title text - "THE BEST PDF"
    cover_content += f"BT\n/F2 48 Tf\n1 1 1 rg\n100 500 Td\n(The Best PDF) Tj\nET\n"

    # Subtitle - "IN THE WORLD"
    cover_content += f"BT\n/F2 32 Tf\n1 0.843 0 rg\n125 440 Td\n(in the World) Tj\nET\n"

    # Decorative line
    cover_content += pdf._color_cmd(255, 215, 0)
    cover_content += "1.5 w\n"
    cover_content += "150 420 m 445 420 l S\n"

    # Subtitle text
    cover_content += f"BT\n/F1 12 Tf\n0.78 0.78 0.86 rg\n80 380 Td\n(A Visual Masterpiece Generated with Python) Tj\nET\n"

    cover_content += f"BT\n/F1 10 Tf\n0.71 0.71 0.78 rg\n100 360 Td\n(Without using any PDF generation tool) Tj\nET\n"

    # Bottom tagline
    cover_content += f"BT\n/F1 9 Tf\n0.59 0.59 0.71 rg\n100 320 Td\n(Art  -  Science  -  Design  -  Technology  -  Beauty) Tj\nET\n"

    cover_content += f"BT\n/F1 8 Tf\n0.47 0.47 0.63 rg\n220 300 Td\n(2026 Edition) Tj\nET\n"

    cover_page_id = pdf._add_page_with_content(595.28, 841.89, cover_content, font_refs)

    # ============================================================
    # PAGE 2: GEOMETRY
    # ============================================================
    geo_content = ""

    # Background
    geo_content += pdf._color_cmd(250, 248, 245, stroke=False)
    geo_content += "0 0 595.28 841.89 re f\n"

    # Title
    geo_content += f"BT\n/F2 28 Tf\n{dec_to_rgb(20, 30, 60)} rg\n30 780 Td\n(The Art of Geometry) Tj\nET\n"

    # Underline
    geo_content += pdf._color_cmd(255, 127, 80, stroke=False)
    geo_content += "30 768 180 4 re f\n"

    # Concentric circles (approximated with round rects)
    geo_content += "0.25 0.41 0.88 RG\n"
    geo_content += "0.5 w\n"
    for r in range(15, 90, 10):
        geo_content += f"{150 - r} {530 - r} {r*2} {r*2} re S\n"

    # Triangle
    geo_content += pdf._color_cmd(220, 20, 60)
    geo_content += "1.5 w\n"
    geo_content += "150 460 m 90 580 l 210 580 l h S\n"

    # Hexagon
    geo_content += pdf._color_cmd(0, 155, 85)
    geo_content += "420 520 m"
    for i in range(1, 7):
        angle = math.pi / 3 * i - math.pi / 6
        x = 420 + 50 * math.cos(angle)
        y = 520 + 50 * math.sin(angle)
        geo_content += f" {x:.1f} {y:.1f} l"
    geo_content += " h S\n"

    # Text content
    geo_content += f"BT\n/F1 11 Tf\n{dec_to_rgb(40, 40, 40)} rg\n30 400 Td\n(Geometry is the language of the universe. From the spirals of galaxies to the) Tj\n"
    geo_content += "0 -16 Td\n(hexagons of honeycombs, mathematical shapes define the world around us.) Tj\n"
    geo_content += "0 -16 Td\n(Every atom, every crystal, every living cell follows geometric rules that) Tj\n"
    geo_content += "0 -16 Td\n(are both elegant and profound.) Tj\nET\n"

    # Constants table
    geo_content += f"BT\n/F2 12 Tf\n{dec_to_rgb(65, 105, 225)} rg\n30 300 Td\n(Key Geometric Constants:) Tj\nET\n"

    constants = [
        ("Pi", "3.14159...", "Circumference / Diameter"),
        ("Golden Ratio", "1.61803...", "Nature's perfect proportion"),
        ("Euler's e", "2.71828...", "Natural logarithm base"),
        ("Root 2", "1.41421...", "Diagonal of unit square"),
    ]

    y_pos = 275
    for name, val, desc in constants:
        geo_content += f"BT\n/F1 10 Tf\n{dec_to_rgb(0, 128, 128)} rg\n30 {y_pos} Td\n({name}) Tj\nET\n"
        geo_content += f"BT\n/F3 10 Tf\n{dec_to_rgb(220, 20, 60)} rg\n90 {y_pos} Td\n({val}) Tj\nET\n"
        geo_content += f"BT\n/F1 9 Tf\n{dec_to_rgb(150, 150, 150)} rg\n160 {y_pos} Td\n({desc}) Tj\nET\n"
        y_pos -= 22

    geo_page_id = pdf._add_page_with_content(595.28, 841.89, geo_content, font_refs)

    # ============================================================
    # PAGE 3: COLOR THEORY
    # ============================================================
    color_content = ""

    # Background
    color_content += pdf._color_cmd(252, 252, 252, stroke=False)
    color_content += "0 0 595.28 841.89 re f\n"

    # Title
    color_content += f"BT\n/F2 28 Tf\n{dec_to_rgb(20, 30, 60)} rg\n30 780 Td\n(Color Theory and Palettes) Tj\nET\n"

    # Underline
    color_content += pdf._color_cmd(255, 105, 180, stroke=False)
    color_content += "30 768 180 4 re f\n"

    # Color wheel (simplified - colored rectangles in a circle pattern)
    cx, cy = 180, 520
    for i in range(24):
        angle_start = math.pi * 2 * i / 24
        angle_end = math.pi * 2 * (i + 1) / 24
        hue = i * 15
        h = hue / 60
        x = int(255 * (1 - abs(h % 2 - 1)))
        if h < 1:
            r, g, b = 255, x, 0
        elif h < 2:
            r, g, b = x, 255, 0
        elif h < 3:
            r, g, b = 0, 255, x
        elif h < 4:
            r, g, b = 0, x, 255
        elif h < 5:
            r, g, b = x, 0, 255
        else:
            r, g, b = 255, 0, x

        color_content += pdf._color_cmd(r, g, b, stroke=False)
        color_content += f"{cx} {cy} m\n"
        steps = 6
        for s in range(steps + 1):
            a = angle_start + (angle_end - angle_start) * s / steps
            px = cx + 70 * math.cos(a)
            py = cy + 70 * math.sin(a)
            color_content += f"{px:.1f} {py:.1f} l\n"
        color_content += "h f\n"

    # Center circle
    color_content += "1 1 1 rg\n"
    color_content += f"{cx} {cy} 30 0 360 arc f\n"

    # Color palettes on the right
    palettes = [
        ("Ocean", [(0, 105, 148), (0, 149, 182), (0, 191, 255), (135, 206, 235), (176, 224, 230)]),
        ("Sunset", [(255, 94, 77), (255, 154, 0), (255, 206, 84), (255, 99, 71), (255, 69, 0)]),
        ("Forest", [(34, 139, 34), (60, 179, 113), (46, 125, 50), (102, 187, 106), (165, 214, 167)]),
        ("Berry", [(156, 39, 176), (171, 71, 188), (206, 147, 216), (234, 128, 252), (123, 31, 162)]),
    ]

    py_pos = 700
    for name, colors in palettes:
        color_content += f"BT\n/F2 10 Tf\n{dec_to_rgb(40, 40, 40)} rg\n370 {py_pos} Td\n({name}) Tj\nET\n"
        px_pos = 370
        for c in colors:
            color_content += pdf._color_cmd(c[0], c[1], c[2], stroke=False)
            color_content += f"{px_pos} {py_pos - 20} 30 15 re f\n"
            px_pos += 33
        py_pos -= 45

    # Text
    color_content += f"BT\n/F1 11 Tf\n{dec_to_rgb(40, 40, 40)} rg\n30 280 Td\n(Color is not merely decorative - it is communicative. Every hue carries) Tj\n"
    color_content += "0 -16 Td\n(psychological weight, cultural meaning, and emotional resonance.) Tj\n"
    color_content += "0 -16 Td\n(The color wheel, first organized by Isaac Newton in 1704, remains) Tj\n"
    color_content += "0 -16 Td\n(the fundamental tool for understanding chromatic relationships.) Tj\nET\n"

    # Color harmony rules
    color_content += f"BT\n/F2 11 Tf\n{dec_to_rgb(75, 0, 130)} rg\n30 200 Td\n(Color Harmony Rules:) Tj\nET\n"

    rules = [
        "Complementary - Opposite colors create maximum contrast",
        "Analogous - Adjacent colors create serene designs",
        "Triadic - Three evenly spaced colors offer vibrant harmony",
        "Split-Complementary - Base + two adjacent to complement",
    ]

    ry = 175
    for rule in rules:
        color_content += pdf._color_cmd(255, 215, 0, stroke=False)
        color_content += f"32 {ry + 4} 6 6 re f\n"
        color_content += f"BT\n/F1 9 Tf\n{dec_to_rgb(40, 40, 40)} rg\n44 {ry} Td\n({rule}) Tj\nET\n"
        ry -= 20

    color_page_id = pdf._add_page_with_content(595.28, 841.89, color_content, font_refs)

    # ============================================================
    # PAGE 4: GOLDEN RATIO
    # ============================================================
    gold_content = ""

    # Background
    gold_content += pdf._color_cmd(255, 253, 245, stroke=False)
    gold_content += "0 0 595.28 841.89 re f\n"

    # Title
    gold_content += f"BT\n/F2 28 Tf\n{dec_to_rgb(20, 30, 60)} rg\n30 780 Td\n(The Golden Ratio) Tj\nET\n"

    # Gold underline
    gold_content += pdf._color_cmd(255, 215, 0, stroke=False)
    gold_content += "30 768 180 4 re f\n"

    # Golden spiral (Fibonacci spiral approximation)
    gold_content += pdf._color_cmd(220, 20, 60)
    gold_content += "1.5 w\n"
    cx, cy = 150, 500
    spiral_pts = []
    for i in range(300):
        t = i / 300.0 * math.pi * 3
        r = 5 * math.pow(1.618, t / (math.pi / 2))
        x = cx + r * math.cos(t) * 0.8
        y = cy - r * math.sin(t) * 0.8
        spiral_pts.append((x, y))

    if spiral_pts:
        gold_content += f"{spiral_pts[0][0]:.1f} {spiral_pts[0][1]:.1f} m\n"
        for px, py in spiral_pts[1:]:
            gold_content += f"{px:.1f} {py:.1f} l\n"
        gold_content += "S\n"

    # Golden rectangles
    gold_content += pdf._color_cmd(255, 215, 0)
    gold_content += "0.8 w\n"
    w, h = 80, 80 / 1.618
    gold_content += f"{cx - w/2:.1f} {cy - h/2:.1f} {w:.1f} {h:.1f} re S\n"

    # Fibonacci sequence
    gold_content += f"BT\n/F2 14 Tf\n{dec_to_rgb(255, 215, 0)} rg\n370 650 Td\n(Fibonacci Sequence) Tj\nET\n"

    gold_content += f"BT\n/F3 12 Tf\n{dec_to_rgb(40, 40, 40)} rg\n370 625 Td\n(1  1  2  3  5  8  13  21  34  55  89) Tj\nET\n"

    gold_content += f"BT\n/F1 10 Tf\n{dec_to_rgb(150, 150, 150)} rg\n370 605 Td\n(Each number = sum of two before it) Tj\nET\n"

    # Formula
    gold_content += f"BT\n/F2 12 Tf\n{dec_to_rgb(0, 128, 128)} rg\n370 560 Td\n(phi = (1 + root 5) / 2 = 1.6180339887...) Tj\nET\n"

    # Text
    gold_content += f"BT\n/F1 11 Tf\n{dec_to_rgb(40, 40, 40)} rg\n30 380 Td\n(The Golden Ratio, denoted by the Greek letter phi, is perhaps the most) Tj\n"
    gold_content += "0 -16 Td\n(famous number in art and nature. It appears in the Parthenon's proportions,) Tj\n"
    gold_content += "0 -16 Td\n(in Leonardo da Vinci's Vitruvian Man, in the spiral of nautilus shells,) Tj\n"
    gold_content += "0 -16 Td\n(and in the arrangement of sunflower seeds.) Tj\n"
    gold_content += "0 -16 Td\n(As the Fibonacci sequence progresses, the ratio of consecutive terms) Tj\n"
    gold_content += "0 -16 Td\n(converges on phi - a beautiful bridge between discrete and continuous.) Tj\nET\n"

    # Quote
    gold_content += f"BT\n/F4 10 Tf\n{dec_to_rgb(150, 150, 150)} rg\n30 250 Td\n('Where there is matter, there is geometry.' - Johannes Kepler) Tj\nET\n"

    gold_page_id = pdf._add_page_with_content(595.28, 841.89, gold_content, font_refs)

    # ============================================================
    # PAGE 5: DATA VISUALIZATION
    # ============================================================
    data_content = ""

    # Background
    data_content += pdf._color_cmd(248, 250, 252, stroke=False)
    data_content += "0 0 595.28 841.89 re f\n"

    # Title
    data_content += f"BT\n/F2 28 Tf\n{dec_to_rgb(20, 30, 60)} rg\n30 780 Td\n(Data Visualization) Tj\nET\n"

    data_content += pdf._color_cmd(0, 155, 85, stroke=False)
    data_content += "30 768 180 4 re f\n"

    # Bar chart
    chart_x, chart_y = 50, 480
    chart_w, chart_h = 220, 180

    # Chart background
    data_content += pdf._color_cmd(255, 255, 255, stroke=False)
    data_content += f"{chart_x} {chart_y} {chart_w} {chart_h} re f\n"

    # Grid lines
    data_content += "0.85 0.85 0.85 RG\n"
    data_content += "0.3 w\n"
    for i in range(5):
        y = chart_y + chart_h * i / 4
        data_content += f"{chart_x} {y} m {chart_x + chart_w} {y} l S\n"

    # Bars
    values = [0.7, 0.85, 0.45, 0.92, 0.63, 0.78]
    labels = ["Art", "Music", "Math", "Nature", "Code", "Design"]
    bar_colors = [
        (65, 105, 225), (255, 127, 80), (255, 215, 0),
        (0, 155, 85), (75, 0, 130), (0, 128, 128)
    ]
    bar_w = chart_w / len(values) * 0.6
    gap = chart_w / len(values)

    for i, (val, label, color) in enumerate(zip(values, labels, bar_colors)):
        bx = chart_x + gap * i + gap * 0.2
        bh = chart_h * val
        data_content += pdf._color_cmd(color[0], color[1], color[2], stroke=False)
        data_content += f"{bx} {chart_y} {bar_w} {bh} re f\n"

        # Label
        data_content += f"BT\n/F1 7 Tf\n{dec_to_rgb(100, 100, 100)} rg\n{bx} {chart_y - 15} Td\n({label}) Tj\nET\n"

    # Chart title
    data_content += f"BT\n/F2 10 Tf\n{dec_to_rgb(40, 40, 40)} rg\n{chart_x} {chart_y + chart_h + 12} Td\n(Beauty Ratings by Discipline) Tj\nET\n"

    # Pie chart
    pie_x, pie_y = 420, 560
    pie_r = 65

    pie_data = [
        ("Visual", 35, (65, 105, 225)),
        ("Auditory", 25, (255, 127, 80)),
        ("Kinesthetic", 20, (0, 155, 85)),
        ("Intellectual", 20, (255, 215, 0)),
    ]

    start_angle = 0
    for label, pct, color in pie_data:
        sweep = pct / 100.0 * 360
        data_content += pdf._color_cmd(color[0], color[1], color[2], stroke=False)
        data_content += f"{pie_x} {pie_y} m\n"
        steps = int(sweep / 5) + 1
        for s in range(steps + 1):
            a = math.radians(start_angle + min(s * 5, sweep))
            px = pie_x + pie_r * math.cos(a)
            py = pie_y + pie_r * math.sin(a)
            data_content += f"{px:.1f} {py:.1f} l\n"
        data_content += "h f\n"
        start_angle += sweep

    # Pie outline
    data_content += "1 1 1 RG\n"
    data_content += "0.5 w\n"
    data_content += f"{pie_x} {pie_y} {pie_r} 0 360 arc S\n"

    # Legend
    ly = 470
    for label, pct, color in pie_data:
        data_content += pdf._color_cmd(color[0], color[1], color[2], stroke=False)
        data_content += f"350 {ly} 10 10 re f\n"
        data_content += f"BT\n/F1 9 Tf\n{dec_to_rgb(40, 40, 40)} rg\n368 {ly} Td\n({label} - {pct}%) Tj\nET\n"
        ly -= 22

    # Text
    data_content += f"BT\n/F1 11 Tf\n{dec_to_rgb(40, 40, 40)} rg\n30 380 Td\n(Data visualization transforms abstract numbers into visual stories.) Tj\n"
    data_content += "0 -16 Td\n(The best charts don't just display data - they reveal patterns,) Tj\n"
    data_content += "0 -16 Td\n(challenge assumptions, and inspire action.) Tj\n"
    data_content += "0 -16 Td\n(From Florence Nightingale's rose diagrams to modern dashboards,) Tj\n"
    data_content += "0 -16 Td\n(visual data representation remains one of humanity's most powerful tools.) Tj\nET\n"

    data_page_id = pdf._add_page_with_content(595.28, 841.89, data_content, font_refs)

    # ============================================================
    # PAGE 6: TYPOGRAPHY
    # ============================================================
    typo_content = ""

    # Background
    typo_content += pdf._color_cmd(252, 250, 248, stroke=False)
    typo_content += "0 0 595.28 841.89 re f\n"

    # Title
    typo_content += f"BT\n/F2 28 Tf\n{dec_to_rgb(20, 30, 60)} rg\n30 780 Td\n(Typography and Design) Tj\nET\n"

    typo_content += pdf._color_cmd(75, 0, 130, stroke=False)
    typo_content += "30 768 180 4 re f\n"

    # Alphabet showcase
    typo_content += f"BT\n/F2 14 Tf\n{dec_to_rgb(40, 40, 40)} rg\n30 700 Td\n(ABCDEFGHIJKLMNOPQRSTUVWXYZ) Tj\nET\n"
    typo_content += f"BT\n/F2 14 Tf\n{dec_to_rgb(40, 40, 40)} rg\n30 675 Td\n(abcdefghijklmnopqrstuvwxyz) Tj\nET\n"
    typo_content += f"BT\n/F2 14 Tf\n{dec_to_rgb(40, 40, 40)} rg\n30 650 Td\n(0123456789 !@#$%&*()) Tj\nET\n"

    # Size showcase
    sizes = [8, 10, 12, 14, 18, 24, 36]
    sy = 610
    for size in sizes:
        r_c = min(40 + size * 3, 200)
        g_c = min(40 + size * 2, 200)
        b_c = min(60 + size * 2, 200)
        typo_content += f"BT\n/F1 {size} Tf\n{dec_to_rgb(r_c, g_c, b_c)} rg\n30 {sy} Td\n(Size {size} - The quick brown fox jumps over the lazy dog) Tj\nET\n"
        sy -= size + 6

    # Design principles boxes
    principles = [
        ("Balance", "Visual equilibrium through symmetry or asymmetry", (65, 105, 225)),
        ("Contrast", "Difference creates visual interest and hierarchy", (220, 20, 60)),
        ("Rhythm", "Repetition creates movement and pattern", (0, 155, 85)),
        ("Unity", "All elements work together as a cohesive whole", (75, 0, 130)),
    ]

    box_w = 130
    for i, (title, desc, color) in enumerate(principles):
        x = 10 + i * 145
        # Box header
        typo_content += pdf._color_cmd(color[0], color[1], color[2], stroke=False)
        typo_content += f"{x} 370 {box_w} 22 re f\n"
        typo_content += f"BT\n/F2 10 Tf\n1 1 1 rg\n{x + 5} 376 Td\n({title}) Tj\nET\n"

        # Box body
        typo_content += pdf._color_cmd(250, 250, 250, stroke=False)
        typo_content += f"{x} 300 {box_w} 70 re f\n"
        typo_content += pdf._color_cmd(color[0], color[1], color[2])
        typo_content += "0.3 w\n"
        typo_content += f"{x} 300 {box_w} 70 re S\n"

        typo_content += f"BT\n/F1 8 Tf\n{dec_to_rgb(40, 40, 40)} rg\n{x + 5} 355 Td\n({desc}) Tj\nET\n"

    # Quote
    typo_content += f"BT\n/F4 10 Tf\n{dec_to_rgb(150, 150, 150)} rg\n30 260 Td\n('Design is not just what it looks like. Design is how it works.' - Steve Jobs) Tj\nET\n"

    typo_page_id = pdf._add_page_with_content(595.28, 841.89, typo_content, font_refs)

    # ============================================================
    # PAGE 7: FRACTALS
    # ============================================================
    frac_content = ""

    # Background
    frac_content += pdf._color_cmd(245, 248, 255, stroke=False)
    frac_content += "0 0 595.28 841.89 re f\n"

    # Title
    frac_content += f"BT\n/F2 28 Tf\n{dec_to_rgb(20, 30, 60)} rg\n30 780 Td\n(Fractals and Patterns) Tj\nET\n"

    frac_content += pdf._color_cmd(0, 128, 128, stroke=False)
    frac_content += "30 768 180 4 re f\n"

    # Sierpinski triangle
    def sierpinski(content, x, y, size, depth, max_depth=5):
        if depth > max_depth:
            return content
        h = size * math.sqrt(3) / 2
        intensity = 80 + depth * 30
        content += f"{intensity/255*0.33:.3f} {intensity/255*0.42:.3f} {intensity/255:.3f} RG\n"
        content += "0.5 w\n"
        content += f"{x} {y - h*2/3:.1f} m {x - size/2:.1f} {y + h/3:.1f} l {x + size/2:.1f} {y + h/3:.1f} l h S\n"

        new_size = size / 2
        content = sierpinski(content, x - size/4, y - h/6, new_size, depth + 1, max_depth)
        content = sierpinski(content, x + size/4, y - h/6, new_size, depth + 1, max_depth)
        content = sierpinski(content, x, y + h/3, new_size, depth + 1, max_depth)
        return content

    frac_content = sierpinski(frac_content, 150, 520, 80, 1)

    # Concentric circles pattern (Mandelbrot-inspired)
    for i in range(20, 0, -1):
        ratio = i / 20
        r = int(20 + ratio * 100)
        g = int(50 + ratio * 80)
        b = int(150 + ratio * 80)
        frac_content += pdf._color_cmd(r, g, b, stroke=False)
        frac_content += f"420 500 {i * 3:.1f} 0 360 arc f\n"

    # Wave patterns
    frac_content += pdf._color_cmd(255, 127, 80)
    frac_content += "0.8 w\n"
    for wave in range(5):
        wy = 320 + wave * 15
        frac_content += f"40 {wy} m\n"
        for x in range(40, 560, 4):
            y = wy + 8 * math.sin((x + wave * 40) * 0.05) * math.cos(wave * 0.3)
            frac_content += f"{x} {y:.1f} l\n"
        frac_content += "S\n"

    # Text
    frac_content += f"BT\n/F1 11 Tf\n{dec_to_rgb(40, 40, 40)} rg\n30 220 Td\n(Fractals are shapes that repeat at every scale - zoom in, and you find) Tj\n"
    frac_content += "0 -16 Td\n(the same pattern repeating infinitely. Discovered by Benoit Mandelbrot) Tj\n"
    frac_content += "0 -16 Td\n(in 1975, fractals describe coastlines, mountain ranges, blood vessels,) Tj\n"
    frac_content += "0 -16 Td\n(and even stock market fluctuations.) Tj\n"
    frac_content += "0 -16 Td\n(They reveal a profound truth: infinite complexity from simple rules.) Tj\nET\n"

    # Formula
    frac_content += f"BT\n/F3 12 Tf\n{dec_to_rgb(0, 128, 128)} rg\n30 130 Td\n(z = z^2 + c) Tj\nET\n"
    frac_content += f"BT\n/F1 9 Tf\n{dec_to_rgb(150, 150, 150)} rg\n30 110 Td\n(The Mandelbrot Set equation) Tj\nET\n"

    frac_page_id = pdf._add_page_with_content(595.28, 841.89, frac_content, font_refs)

    # ============================================================
    # PAGE 8: LIGHT SCIENCE
    # ============================================================
    light_content = ""

    # Background
    light_content += pdf._color_cmd(240, 248, 255, stroke=False)
    light_content += "0 0 595.28 841.89 re f\n"

    # Title
    light_content += f"BT\n/F2 28 Tf\n{dec_to_rgb(20, 30, 60)} rg\n30 780 Td\n(The Science of Light) Tj\nET\n"

    light_content += pdf._color_cmd(135, 206, 235, stroke=False)
    light_content += "30 768 180 4 re f\n"

    # Electromagnetic spectrum
    spectrum_x, spectrum_y = 40, 580
    spectrum_w, spectrum_h = 500, 30

    for i in range(int(spectrum_w)):
        ratio = i / spectrum_w
        if ratio < 0.15:
            r, g, b = 148, 0, 211
        elif ratio < 0.25:
            r, g, b = 75, 0, 130
        elif ratio < 0.4:
            r, g, b = 0, 0, 255
        elif ratio < 0.55:
            r, g, b = 0, 255, 0
        elif ratio < 0.7:
            r, g, b = 255, 255, 0
        elif ratio < 0.85:
            r, g, b = 255, 127, 0
        else:
            r, g, b = 255, 0, 0

        light_content += pdf._color_cmd(r, g, b, stroke=False)
        light_content += f"{spectrum_x + i} {spectrum_y} 1 {spectrum_h} re f\n"

    # Spectrum label
    light_content += f"BT\n/F2 10 Tf\n{dec_to_rgb(40, 40, 40)} rg\n{spectrum_x} {spectrum_y + spectrum_h + 12} Td\n(The Visible Electromagnetic Spectrum \\(380nm - 700nm\\)) Tj\nET\n"

    # Light facts boxes
    facts = [
        ("Speed of Light", "299,792,458 m/s\nThe cosmic speed limit", (255, 215, 0)),
        ("Photon Energy", "E = hf\nLight as particles", (255, 127, 80)),
        ("Wavelength", "lambda = c/f\nColor as frequency", (0, 155, 85)),
        ("Refraction", "n = c/v\nLight bends in media", (65, 105, 225)),
    ]

    for i, (title, content, color) in enumerate(facts):
        x = 10 + i * 145
        # Header
        light_content += pdf._color_cmd(color[0], color[1], color[2], stroke=False)
        light_content += f"{x} 480 135 22 re f\n"
        light_content += f"BT\n/F2 10 Tf\n1 1 1 rg\n{x + 5} 486 Td\n({title}) Tj\nET\n"

        # Body
        light_content += pdf._color_cmd(250, 250, 250, stroke=False)
        light_content += f"{x} 410 135 70 re f\n"
        light_content += pdf._color_cmd(color[0], color[1], color[2])
        light_content += "0.3 w\n"
        light_content += f"{x} 410 135 70 re S\n"

        light_content += f"BT\n/F1 8 Tf\n{dec_to_rgb(40, 40, 40)} rg\n{x + 5} 465 Td\n({content}) Tj\nET\n"

    # Text
    light_content += f"BT\n/F1 11 Tf\n{dec_to_rgb(40, 40, 40)} rg\n30 350 Td\n(Light is the bridge between the invisible and the visible. What we call) Tj\n"
    light_content += "0 -16 Td\n('visible light' is a tiny sliver of the electromagnetic spectrum - just) Tj\n"
    light_content += "0 -16 Td\n(wavelengths between 380 and 700 nanometers. Beyond red lies infrared,) Tj\n"
    light_content += "0 -16 Td\n(microwaves, and radio waves. Beyond violet: ultraviolet, X-rays, and) Tj\n"
    light_content += "0 -16 Td\n(gamma rays. The entire cosmos speaks in light; we learned to listen.) Tj\nET\n"

    # Quote
    light_content += f"BT\n/F4 10 Tf\n{dec_to_rgb(150, 150, 150)} rg\n30 230 Td\n('Nothing travels faster than light, except bad news.' - Douglas Adams) Tj\nET\n"

    light_page_id = pdf._add_page_with_content(595.28, 841.89, light_content, font_refs)

    # ============================================================
    # PAGE 9: CONCLUSION
    # ============================================================
    conc_content = ""

    # Background gradient
    for i in range(100):
        ratio = i / 100.0
        r = int(20 + ratio * 55)
        g = int(30 + ratio * 0)
        b = int(60 + ratio * 70)
        conc_content += pdf._color_cmd(r, g, b, stroke=False)
        conc_content += f"0 {i * 8.4:.1f} 595.28 8.5 re f\n"

    # Decorative circles
    conc_content += "1 1 1 rg\n"
    conc_content += "-30 -30 180 180 re f\n"

    conc_content += pdf._color_cmd(255, 215, 0, stroke=False)
    conc_content += "480 700 140 140 re f\n"

    conc_content += pdf._color_cmd(255, 127, 80, stroke=False)
    conc_content += "500 30 90 90 re f\n"

    conc_content += pdf._color_cmd(0, 128, 128, stroke=False)
    conc_content += "-10 740 110 110 re f\n"

    # Stars
    for pos in [(80, 200), (500, 350), (50, 500), (530, 200), (280, 80)]:
        conc_content += "1 1 1 rg\n"
        conc_content += f"{pos[0]} {pos[1]} 12 12 re f\n"

    # Title
    conc_content += f"BT\n/F2 42 Tf\n1 1 1 rg\n150 480 Td\n(The Journey) Tj\nET\n"
    conc_content += f"BT\n/F2 42 Tf\n1 1 1 rg\n175 420 Td\n(Continues...) Tj\nET\n"

    # Decorative line
    conc_content += pdf._color_cmd(255, 215, 0)
    conc_content += "1.5 w\n"
    conc_content += "150 400 m 445 400 l S\n"

    # Subtitle
    conc_content += f"BT\n/F1 13 Tf\n{dec_to_rgb(200, 200, 220)} rg\n180 360 Td\n(Every end is a new beginning.) Tj\nET\n"
    conc_content += f"BT\n/F1 13 Tf\n{dec_to_rgb(200, 200, 220)} rg\n170 335 Td\n(Every page turned reveals a new world.) Tj\nET\n"

    # Thank you
    conc_content += f"BT\n/F2 18 Tf\n{dec_to_rgb(255, 215, 0)} rg\n220 280 Td\n(Thank You) Tj\nET\n"

    # Credits
    conc_content += f"BT\n/F1 10 Tf\n{dec_to_rgb(150, 150, 180)} rg\n155 230 Td\n(This PDF was generated entirely with raw Python) Tj\nET\n"
    conc_content += f"BT\n/F1 10 Tf\n{dec_to_rgb(150, 150, 180)} rg\n145 210 Td\n(using hand-crafted PDF bytecode - no PDF tools used) Tj\nET\n"
    conc_content += f"BT\n/F1 10 Tf\n{dec_to_rgb(150, 150, 180)} rg\n195 190 Td\n(Created by Kino, your AI agent) Tj\nET\n"
    conc_content += f"BT\n/F1 10 Tf\n{dec_to_rgb(150, 150, 180)} rg\n230 170 Td\n(2026) Tj\nET\n"

    conc_page_id = pdf._add_page_with_content(595.28, 841.89, conc_content, font_refs)

    # ============================================================
    # Update page tree with actual page references
    # ============================================================
    all_pages = [cover_page_id, geo_page_id, color_page_id, gold_page_id,
                 data_page_id, typo_page_id, frac_page_id, light_page_id, conc_page_id]
    kids_str = " ".join(f"{p} 0 R" for p in all_pages)
    page_tree = f"<< /Type /Pages /Kids [{kids_str}] /Count {len(all_pages)} >>"
    # Replace the placeholder
    for i, (oid, content) in enumerate(pdf.objects):
        if oid == pdf.page_tree_id:
            pdf.objects[i] = (oid, page_tree.encode('latin-1'))
            break

    # Write the PDF
    pdf.write()
    print(f"PDF created: {pdf.filename}")
    print(f"Total pages: {len(all_pages)}")
    print(f"Total objects: {pdf.current_obj - 1}")


if __name__ == '__main__':
    create_best_pdf()
