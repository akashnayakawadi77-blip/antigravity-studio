"""
Traveling Panda Export Service
Generates professional PDF documents, high-resolution JPG image summaries, and Microsoft Word (.docx) documents
complete with embedded place images, hotel photos, tables, and branding.
"""
import os
import re
import datetime
from PIL import Image as PILImage, ImageDraw, ImageFont

# ReportLab imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Python-Docx imports
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def clean_markdown_for_pdf(text: str) -> str:
    """Clean markdown syntax for ReportLab Paragraph compatibility."""
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'^#+\s*', '', text)
    text = re.sub(r'</?(div|span|style|iframe)[^>]*>', '', text)
    return text.strip()

def export_to_pdf(destination: str, answers: dict, itinerary_markdown: str, gallery_dict: dict = None) -> bytes:
    """Generates a professional PDF document. Returns binary PDF bytes."""
    out_dir = r"e:\Antigravity\outputs\exports"
    os.makedirs(out_dir, exist_ok=True)
    pdf_file = os.path.join(out_dir, f"TravelingPanda_{destination.replace(' ', '_')}.pdf")

    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=24, leading=28,
        textColor=colors.HexColor('#0f172a'), spaceAfter=6
    )
    
    sub_style = ParagraphStyle(
        'DocSub', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=13, leading=16,
        textColor=colors.HexColor('#16a34a'), spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'Head1', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=15, leading=18,
        textColor=colors.HexColor('#0f172a'), spaceBefore=14, spaceAfter=8
    )

    body_style = ParagraphStyle(
        'BodyDark', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=14,
        textColor=colors.HexColor('#334155'), spaceAfter=6
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph(f"🐼 Traveling Panda Master Guide", title_style))
    story.append(Paragraph(f"Destination: <b>{destination.title()}</b> | Generated on {datetime.datetime.now().strftime('%b %d, %Y')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#e2e8f0'), spaceAfter=14))

    # 2. Trip Overview Table
    overview_data = [
        [Paragraph("<b>Destination</b>", body_style), Paragraph(answers.get("destination", "-"), body_style),
         Paragraph("<b>Dates & Duration</b>", body_style), Paragraph(answers.get("travel_dates", "-"), body_style)],
        [Paragraph("<b>Travelers</b>", body_style), Paragraph(answers.get("travelers", "-"), body_style),
         Paragraph("<b>Budget</b>", body_style), Paragraph(answers.get("budget", "-"), body_style)],
        [Paragraph("<b>Accommodation</b>", body_style), Paragraph(answers.get("stay_preference", "-"), body_style),
         Paragraph("<b>Special Req.</b>", body_style), Paragraph(answers.get("special_requirements", "-"), body_style)],
    ]
    t = Table(overview_data, colWidths=[100, 150, 100, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    # 3. Destination Photos
    if gallery_dict and gallery_dict.get("destination_images"):
        story.append(Paragraph("📸 Destination Highlights", h1_style))
        img_cells = []
        for item in gallery_dict["destination_images"][:3]:
            img_path = item.get("path") if isinstance(item, dict) else item
            if img_path and os.path.exists(img_path):
                try:
                    img_cells.append(RLImage(img_path, width=160, height=105))
                except Exception:
                    pass
        if img_cells:
            img_table = Table([img_cells], colWidths=[170]*len(img_cells))
            img_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('PADDING', (0,0), (-1,-1), 2),
            ]))
            story.append(img_table)
            story.append(Spacer(1, 14))

    # 4. Main Itinerary
    lines = itinerary_markdown.split('\n')
    for line in lines:
        line_s = line.strip()
        if not line_s: continue
        if line_s.startswith('# ') or line_s.startswith('## '):
            story.append(Paragraph(clean_markdown_for_pdf(line_s), h1_style))
        elif line_s.startswith('### '):
            story.append(Paragraph(clean_markdown_for_pdf(line_s), ParagraphStyle('Head2', parent=h1_style, fontSize=12, leading=15, textColor=colors.HexColor('#16a34a'))))
        elif line_s.startswith('|'):
            continue
        else:
            story.append(Paragraph(clean_markdown_for_pdf(line_s), body_style))

    # 5. Hotel Photos Table
    if gallery_dict and gallery_dict.get("hotel_images"):
        story.append(Spacer(1, 14))
        story.append(Paragraph("🏨 Suggested Accommodations & Photos", h1_style))
        hotel_rows = []
        for h_item in gallery_dict["hotel_images"]:
            h_name = h_item.get("name", "Recommended Hotel")
            h_path = h_item.get("path")
            cell_txt = Paragraph(f"<b>{h_name}</b><br><font color='#64748b'>Selected for your stay preference</font>", body_style)
            cell_img = RLImage(h_path, width=120, height=80) if h_path and os.path.exists(h_path) else Paragraph("-", body_style)
            hotel_rows.append([cell_img, cell_txt])
        
        if hotel_rows:
            ht_table = Table(hotel_rows, colWidths=[130, 380])
            ht_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ]))
            story.append(ht_table)

    doc.build(story)

    with open(pdf_file, "rb") as f:
        return f.read()

def wrap_text(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw) -> list:
    """Wraps text into lines that fit within max_width pixels."""
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        try:
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
        except Exception:
            w = len(test_line) * 10
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return lines or [text]

def export_to_jpg(destination: str, answers: dict, itinerary_markdown: str, gallery_dict: dict = None) -> bytes:
    """
    Renders a full-detail high-resolution JPG image document with dynamic height.
    Includes complete itinerary days, places, food guide, budget tables, hotel photos, and maps info.
    Returns binary JPG bytes.
    """
    out_dir = r"e:\Antigravity\outputs\exports"
    os.makedirs(out_dir, exist_ok=True)
    jpg_file = os.path.join(out_dir, f"TravelingPanda_{destination.replace(' ', '_')}.jpg")

    W = 1080
    left_m = 40
    right_m = W - 40
    max_w = right_m - left_m

    try:
        font_header = ImageFont.truetype("arialbd.ttf", 36)
        font_sub    = ImageFont.truetype("arialbd.ttf", 22)
        font_h1     = ImageFont.truetype("arialbd.ttf", 22)
        font_h2     = ImageFont.truetype("arialbd.ttf", 19)
        font_body   = ImageFont.truetype("arial.ttf", 16)
        font_bold   = ImageFont.truetype("arialbd.ttf", 16)
        font_small  = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        font_header = font_sub = font_h1 = font_h2 = font_body = font_bold = font_small = ImageFont.load_default()

    dummy_img = PILImage.new("RGB", (100, 100))
    draw_meas = ImageDraw.Draw(dummy_img)

    lines = itinerary_markdown.split('\n')

    # Pass 1: Measure total height
    y = 160  # Header
    y += 180  # Trip summary box

    dest_imgs = gallery_dict.get("destination_images", []) if gallery_dict else []
    valid_dest_imgs = [item for item in dest_imgs[:3] if (item.get("path") if isinstance(item, dict) else item) and os.path.exists(item.get("path") if isinstance(item, dict) else item)]
    if valid_dest_imgs:
        y += 240

    for l in lines:
        l_s = l.strip()
        if not l_s:
            y += 8
            continue
        clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', l_s)
        clean_line = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_line)

        if l_s.startswith('# ') or l_s.startswith('## '):
            w_lines = wrap_text(clean_line.replace('#', '').strip(), font_h1, max_w, draw_meas)
            y += len(w_lines) * 38 + 16
        elif l_s.startswith('### '):
            w_lines = wrap_text(clean_line.replace('#', '').strip(), font_h2, max_w, draw_meas)
            y += len(w_lines) * 28 + 12
        elif l_s.startswith('|'):
            y += 32
        else:
            w_lines = wrap_text(clean_line, font_body, max_w - 20, draw_meas)
            y += len(w_lines) * 24 + 6

    hotel_imgs = gallery_dict.get("hotel_images", []) if gallery_dict else []
    valid_hotel_imgs = [item for item in hotel_imgs[:3] if (item.get("path") if isinstance(item, dict) else item) and os.path.exists(item.get("path") if isinstance(item, dict) else item)]
    if valid_hotel_imgs:
        y += 260

    y += 100  # Footer

    total_H = max(1600, int(y))

    # Pass 2: Draw full image
    img = PILImage.new("RGB", (W, total_H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 1. Header Banner
    draw.rectangle([0, 0, W, 140], fill=(15, 23, 42))
    draw.text((left_m, 32), "🐼 Traveling Panda Master Travel Guide", fill=(255, 255, 255), font=font_header)
    draw.text((left_m, 86), f"Destination: {destination.title()} | Generated on {datetime.datetime.now().strftime('%b %d, %Y')}", fill=(52, 211, 153), font=font_sub)

    cur_y = 155

    # 2. Trip Overview Card
    draw.rounded_rectangle([left_m, cur_y, right_m, cur_y + 160], radius=14, fill=(248, 250, 252), outline=(203, 213, 225), width=2)
    col1_x = left_m + 20
    col2_x = left_m + 500

    draw.text((col1_x, cur_y + 18), f"📍 Starting From: {answers.get('origin_city', '-')}", fill=(15, 23, 42), font=font_bold)
    draw.text((col2_x, cur_y + 18), f"🗺️ Destination: {answers.get('destination', '-')}", fill=(15, 23, 42), font=font_bold)

    draw.text((col1_x, cur_y + 54), f"📅 Dates & Duration: {answers.get('travel_dates', '-')}", fill=(15, 23, 42), font=font_bold)
    draw.text((col2_x, cur_y + 54), f"👥 Travelers: {answers.get('travelers', '-')}", fill=(15, 23, 42), font=font_bold)

    draw.text((col1_x, cur_y + 90), f"💰 Budget: {answers.get('budget', '-')}", fill=(15, 23, 42), font=font_bold)
    draw.text((col2_x, cur_y + 90), f"🏨 Stay Style: {answers.get('stay_preference', '-')}", fill=(15, 23, 42), font=font_bold)

    draw.text((col1_x, cur_y + 126), f"🙏 Special Reqs: {answers.get('special_requirements', '-')}", fill=(100, 116, 139), font=font_body)

    cur_y += 180

    # 3. Destination Photos Row
    if valid_dest_imgs:
        draw.text((left_m, cur_y), "📸 Destination Highlights & Scenic Spots", fill=(15, 23, 42), font=font_h1)
        cur_y += 36
        img_w = (max_w - (len(valid_dest_imgs) - 1) * 16) // len(valid_dest_imgs)
        for idx, item in enumerate(valid_dest_imgs):
            h_path = item.get("path") if isinstance(item, dict) else item
            h_name = item.get("name", "Spot") if isinstance(item, dict) else "Spot"
            x_pos = left_m + idx * (img_w + 16)
            try:
                p_img = PILImage.open(h_path).convert("RGB")
                p_img = p_img.resize((img_w, 150))
                img.paste(p_img, (x_pos, cur_y))
                draw.rectangle([x_pos, cur_y + 150 - 30, x_pos + img_w, cur_y + 150], fill=(0, 0, 0, 160))
                draw.text((x_pos + 8, cur_y + 150 - 24), h_name[:24], fill=(255, 255, 255), font=font_small)
            except Exception:
                pass
        cur_y += 175

    # 4. Complete Itinerary Content
    for l in lines:
        l_s = l.strip()
        if not l_s:
            cur_y += 8
            continue

        clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', l_s)
        clean_line = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1 (Maps Pin)', clean_line)

        if l_s.startswith('# ') or l_s.startswith('## '):
            cur_y += 10
            h_text = clean_line.replace('#', '').strip()
            w_lines = wrap_text(h_text, font_h1, max_w, draw)
            for wl in w_lines:
                draw.rounded_rectangle([left_m, cur_y, right_m, cur_y + 34], radius=6, fill=(230, 244, 234))
                draw.text((left_m + 12, cur_y + 4), wl, fill=(22, 101, 52), font=font_h1)
                cur_y += 38
        elif l_s.startswith('### '):
            cur_y += 6
            h_text = clean_line.replace('#', '').strip()
            w_lines = wrap_text(h_text, font_h2, max_w, draw)
            for wl in w_lines:
                draw.text((left_m + 6, cur_y), f"• {wl}", fill=(15, 23, 42), font=font_h2)
                cur_y += 28
        elif l_s.startswith('|'):
            row_items = [c.strip() for c in l_s.split('|')[1:-1] if c.strip()]
            if row_items:
                is_header = '---' in l_s or any('---' in c for c in row_items)
                if not is_header:
                    col_w = max_w // len(row_items)
                    for c_idx, cell_t in enumerate(row_items):
                        x_cell = left_m + c_idx * col_w
                        draw.rectangle([x_cell, cur_y, x_cell + col_w - 4, cur_y + 28], fill=(248, 250, 252), outline=(226, 232, 240))
                        draw.text((x_cell + 6, cur_y + 5), cell_t[:25], fill=(51, 65, 85), font=font_small)
                    cur_y += 32
        else:
            w_lines = wrap_text(clean_line, font_body, max_w - 15, draw)
            for wl in w_lines:
                draw.text((left_m + 15, cur_y), wl, fill=(51, 65, 85), font=font_body)
                cur_y += 24
            cur_y += 4

    # 5. Suggested Hotel Photos
    if valid_hotel_imgs:
        cur_y += 15
        draw.text((left_m, cur_y), "🏨 Suggested Accommodations & Hotel Photos", fill=(15, 23, 42), font=font_h1)
        cur_y += 36
        img_w = (max_w - (len(valid_hotel_imgs) - 1) * 16) // len(valid_hotel_imgs)
        for idx, item in enumerate(valid_hotel_imgs):
            h_path = item.get("path") if isinstance(item, dict) else item
            h_name = item.get("name", "Recommended Hotel") if isinstance(item, dict) else "Recommended Hotel"
            x_pos = left_m + idx * (img_w + 16)
            try:
                p_img = PILImage.open(h_path).convert("RGB")
                p_img = p_img.resize((img_w, 150))
                img.paste(p_img, (x_pos, cur_y))
                draw.text((x_pos, cur_y + 154), h_name[:24], fill=(15, 23, 42), font=font_bold)
            except Exception:
                pass
        cur_y += 190

    # 6. Footer Banner
    cur_y = total_H - 80
    draw.rectangle([0, cur_y, W, total_H], fill=(15, 23, 42))
    draw.text((W // 2 - 240, cur_y + 28), "Generated with ❤️ by Traveling Panda Concierge 🐼✈️", fill=(255, 255, 255), font=font_bold)

    img.save(jpg_file, "JPEG", quality=92)
    with open(jpg_file, "rb") as f:
        return f.read()

def export_to_docx(destination: str, answers: dict, itinerary_markdown: str, gallery_dict: dict = None) -> bytes:
    """
    Generates a Microsoft Word (.docx) document with panda header, trip parameters table,
    embedded place photos, formatted markdown headings, and hotel photos table.
    Returns binary DOCX bytes.
    """
    out_dir = r"e:\Antigravity\outputs\exports"
    os.makedirs(out_dir, exist_ok=True)
    docx_file = os.path.join(out_dir, f"TravelingPanda_{destination.replace(' ', '_')}.docx")

    doc = docx.Document()

    # Document Heading
    title_p = doc.add_paragraph()
    run_t = title_p.add_run("🐼 Traveling Panda Master Travel Plan")
    run_t.font.name = "Arial"
    run_t.font.size = Pt(22)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(15, 23, 42)

    sub_p = doc.add_paragraph()
    run_s = sub_p.add_run(f"Destination: {destination.title()} | Generated on {datetime.datetime.now().strftime('%b %d, %Y')}")
    run_s.font.name = "Arial"
    run_s.font.size = Pt(12)
    run_s.font.bold = True
    run_s.font.color.rgb = RGBColor(22, 101, 52)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Summary Overview Table
    table = doc.add_table(rows=3, cols=2)
    table.style = 'Table Grid'
    params = [
        ("Destination", answers.get("destination", "-")),
        ("Dates & Duration", answers.get("travel_dates", "-")),
        ("Travelers", answers.get("travelers", "-")),
        ("Budget", answers.get("budget", "-")),
        ("Accommodation", answers.get("stay_preference", "-")),
        ("Special Requirements", answers.get("special_requirements", "-")),
    ]
    for idx, (k, v) in enumerate(params):
        r_idx = idx // 2
        c_idx = idx % 2
        cell = table.cell(r_idx, c_idx)
        cell.text = f"{k}: {v}"
        for p in cell.paragraphs:
            p.runs[0].font.name = "Arial"
            p.runs[0].font.size = Pt(10)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Destination Photos in Word
    if gallery_dict and gallery_dict.get("destination_images"):
        h_dest = doc.add_paragraph()
        run_hd = h_dest.add_run("📸 Destination Highlights")
        run_hd.font.name = "Arial"
        run_hd.font.size = Pt(14)
        run_hd.font.bold = True
        run_hd.font.color.rgb = RGBColor(15, 23, 42)

        for item in gallery_dict["destination_images"][:4]:
            img_path = item.get("path") if isinstance(item, dict) else item
            if img_path and os.path.exists(img_path):
                try:
                    doc.add_picture(img_path, width=Inches(5.5))
                    doc.add_paragraph().paragraph_format.space_after = Pt(6)
                except Exception:
                    pass

    # Markdown Itinerary Translation
    lines = itinerary_markdown.split('\n')
    for line in lines:
        l_s = line.strip()
        if not l_s:
            continue
        if l_s.startswith('# ') or l_s.startswith('## '):
            p = doc.add_heading(level=1)
            r = p.add_run(re.sub(r'^[#\s]+', '', l_s))
            r.font.name = "Arial"
            r.font.color.rgb = RGBColor(15, 23, 42)
        elif l_s.startswith('### '):
            p = doc.add_heading(level=2)
            r = p.add_run(re.sub(r'^[#\s]+', '', l_s))
            r.font.name = "Arial"
            r.font.color.rgb = RGBColor(22, 101, 52)
        elif l_s.startswith('- ') or l_s.startswith('* '):
            p = doc.add_paragraph(style='List Bullet')
            r = p.add_run(l_s[2:].replace('**', ''))
            r.font.name = "Arial"
            r.font.size = Pt(10.5)
        elif not l_s.startswith('|'):
            p = doc.add_paragraph()
            clean_txt = l_s.replace('**', '')
            r = p.add_run(clean_txt)
            r.font.name = "Arial"
            r.font.size = Pt(10.5)

    # Hotel Photos Section in Word
    if gallery_dict and gallery_dict.get("hotel_images"):
        doc.add_paragraph().paragraph_format.space_after = Pt(12)
        h_hot = doc.add_paragraph()
        run_hh = h_hot.add_run("🏨 Suggested Hotel Photos")
        run_hh.font.name = "Arial"
        run_hh.font.size = Pt(14)
        run_hh.font.bold = True
        run_hh.font.color.rgb = RGBColor(15, 23, 42)

        for h_item in gallery_dict["hotel_images"][:3]:
            h_name = h_item.get("name", "Recommended Hotel")
            h_path = h_item.get("path")
            hp = doc.add_paragraph()
            hrun = hp.add_run(f"Hotel: {h_name}")
            hrun.font.bold = True
            hrun.font.size = Pt(11)
            if h_path and os.path.exists(h_path):
                try:
                    doc.add_picture(h_path, width=Inches(4.5))
                    doc.add_paragraph().paragraph_format.space_after = Pt(6)
                except Exception:
                    pass

    doc.save(docx_file)
    with open(docx_file, "rb") as f:
        return f.read()
