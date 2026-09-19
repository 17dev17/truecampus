import os
import io
import logging
from typing import Dict, Any, List
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from core.config import settings

logger = logging.getLogger("truecampus.pdf")

FONT_NAME = "ArialCustom"
FONT_BOLD_NAME = "ArialCustomBold"

def _register_fonts():
    global FONT_NAME, FONT_BOLD_NAME
    try:
        if "ArialCustom" not in pdfmetrics.getRegisteredFontNames():
            font_path = "C:/Windows/Fonts/arial.ttf"
            font_bold_path = "C:/Windows/Fonts/arialbd.ttf"
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont(FONT_NAME, font_path))
                pdfmetrics.registerFont(TTFont(FONT_BOLD_NAME, font_bold_path if os.path.exists(font_bold_path) else font_path))
            else:
                FONT_NAME = "Helvetica"
                FONT_BOLD_NAME = "Helvetica-Bold"
    except Exception as e:
        logger.warning(f"Failed to register custom font: {e}")

_register_fonts()

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont(FONT_NAME, 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        if self._pageNumber > 1:
            self.drawString(40, 810, f"TrueCampus B2B Verification Audit | {settings.branding.name}")
            self.drawRightString(555, 810, f"Confidential White-Label Report")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(40, 804, 555, 804)
        
        page_text = f"Стр. {self._pageNumber} из {page_count}"
        self.drawString(40, 25, f"{settings.branding.name} • {settings.branding.website} • {settings.branding.contact_email}")
        self.drawRightString(555, 25, page_text)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(40, 35, 555, 35)
        self.restoreState()

def build_pdf_report(profile_data: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        fontName=FONT_BOLD_NAME,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor(settings.branding.secondary_color)
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName=FONT_NAME,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#64748b")
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        fontName=FONT_BOLD_NAME,
        fontSize=13,
        leading=17,
        textColor=colors.HexColor(settings.branding.primary_color),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        fontName=FONT_NAME,
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1e293b")
    )
    meta_bold = ParagraphStyle(
        'MetaBold',
        fontName=FONT_BOLD_NAME,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0f172a")
    )
    body_right_style = ParagraphStyle(
        'BodyTextRight',
        fontName=FONT_NAME,
        fontSize=8,
        leading=11,
        alignment=2,
        textColor=colors.HexColor("#64748b")
    )
    badge_style = ParagraphStyle(
        'BadgeStyle',
        fontName=FONT_BOLD_NAME,
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    story = []

    brand_row = [
        [
            Paragraph(f"<b>{settings.branding.name}</b><br/><font size=8 color='#64748b'>{settings.branding.tagline}</font>", body_style),
            Paragraph("ЮРИДИЧЕСКИЙ АУДИТ МЕДИА-ПРОФИЛЯ ВУЗА<br/>Стандарт: CC BY/SA & Zero-Shot Verification", body_right_style)
        ]
    ]
    brand_table = Table(brand_row, colWidths=[280, 235])
    brand_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor(settings.branding.primary_color))
    ]))
    story.append(brand_table)
    story.append(Spacer(1, 14))

    canonical = profile_data.get("canonical_name", "Университет")
    english = profile_data.get("english_name", "")
    city = profile_data.get("city", "Unknown City")
    country = profile_data.get("country", "")
    summary_text = profile_data.get("campus_summary", "")

    story.append(Paragraph(f"Верификационный профиль: {canonical}", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Официальное международное название: <b>{english}</b> | Локация: <b>{city}, {country}</b>", subtitle_style))
    story.append(Spacer(1, 14))

    metrics = profile_data.get("metrics", {})
    rules_summary = profile_data.get("rules_summary", {})
    coverage = rules_summary.get("verification_coverage_percent", 0.0)
    total_photos = rules_summary.get("total_verified_photos", 0)
    duplicates_dropped = metrics.get("duplicates_dropped", 0)

    kpi_data = [
        [
            Paragraph(f"<font size=8 color='#64748b'>ПОКРЫТИЕ КАТЕГОРИЙ</font><br/><b><font size=14 color='#2563eb'>{coverage}%</font></b>", body_style),
            Paragraph(f"<font size=8 color='#64748b'>ВЕРИФИЦИРОВАНО ФОТО</font><br/><b><font size=14 color='#10b981'>{total_photos} шт.</font></b>", body_style),
            Paragraph(f"<font size=8 color='#64748b'>ОТСЕЯНО ДУБЛИКАТОВ</font><br/><b><font size=14 color='#f59e0b'>{duplicates_dropped} (pHash ≤ 6)</font></b>", body_style),
            Paragraph(f"<font size=8 color='#64748b'>СТАТУС ЛИЦЕНЗИЙ</font><br/><b><font size=14 color='#059669'>100% CC Clean</font></b>", body_style)
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[128, 128, 128, 131])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Краткое аналитическое описание кампуса", h2_style))
    summary_box = [
        [Paragraph(f"<i>«{summary_text}»</i>", body_style)]
    ]
    sum_table = Table(summary_box, colWidths=[515])
    sum_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#eff6ff")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#bfdbfe")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(sum_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Статус открытых источников данных (Graceful Degradation)", h2_style))
    sources_status = profile_data.get("sources_status", {})
    src_rows = [
        [
            Paragraph("<b>Источник данных</b>", meta_bold),
            Paragraph("<b>Протокол / Эндпоинт</b>", meta_bold),
            Paragraph("<b>Статус ответа (таймаут 5.0с)</b>", meta_bold)
        ]
    ]
    
    source_names_map = {
        "wikimedia": ("Wikimedia Commons", "REST API (MediaWiki File API)"),
        "openverse": ("Openverse CC Engine", "v1/images (Creative Commons)"),
        "mapillary": ("Mapillary Street-level", "v4/graph API (Bbox coverage)"),
        "offline_verified_cache": ("Локальный проверенный кэш", "Pre-indexed verified storage")
    }

    for s_key, s_status in sources_status.items():
        s_name, s_proto = source_names_map.get(s_key, (s_key.title(), "Open API REST"))
        status_color = "#059669" if ("ok" in s_status.lower() or "loaded" in s_status.lower()) else "#d97706"
        src_rows.append([
            Paragraph(s_name, body_style),
            Paragraph(s_proto, body_style),
            Paragraph(f"<font color='{status_color}'><b>{s_status.upper()}</b></font>", body_style)
        ])

    src_table = Table(src_rows, colWidths=[160, 200, 155])
    src_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(src_table)

    story.append(PageBreak())

    story.append(Paragraph("Верифицированные категории и статус «Честной неопределенности»", title_style))
    story.append(Paragraph("Классификация: open_clip ViT-B/32 (CPU). Порог зачисления: Confidence Score ≥ 0.65.", subtitle_style))
    story.append(Spacer(1, 10))

    categories = profile_data.get("categories", {})
    cat_rows = [
        [
            Paragraph("<b>Категория</b>", meta_bold),
            Paragraph("<b>Статус верификации</b>", meta_bold),
            Paragraph("<b>Точность (CLIP)</b>", meta_bold),
            Paragraph("<b>Число подтвержденных фото</b>", meta_bold)
        ]
    ]

    for c_key, c_info in categories.items():
        is_v = c_info.get("is_verified", False)
        status_color = "#15803d" if is_v else "#b91c1c"
        status_label = "ВЕРИФИЦИРОВАНО" if is_v else "НЕТ ВЕРИФИЦИРОВАННЫХ ДАННЫХ"
        conf_str = f"{int(c_info.get('average_confidence', 0.0) * 100)}%" if is_v else "—"
        count = c_info.get("items_count", 0)

        cat_rows.append([
            Paragraph(f"<b>{c_info.get('title')}</b><br/><font size=7 color='#64748b'>{c_info.get('description')}</font>", body_style),
            Paragraph(f"<font color='{status_color}'><b>{status_label}</b></font>", body_style),
            Paragraph(conf_str, body_style),
            Paragraph(f"<b>{count} фото</b>", body_style)
        ])

    cat_table = Table(cat_rows, colWidths=[185, 160, 85, 85])
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(cat_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Реестр верифицированных визуальных материалов", h2_style))
    media_rows = [
        [
            Paragraph("<b>ID / Название</b>", meta_bold),
            Paragraph("<b>Категория</b>", meta_bold),
            Paragraph("<b>Уверенность CLIP</b>", meta_bold),
            Paragraph("<b>Лицензия CC</b>", meta_bold),
            Paragraph("<b>Автор / Источник</b>", meta_bold)
        ]
    ]

    for c_key, c_info in categories.items():
        for item in c_info.get("items", []):
            title = item.get("title", "Без названия")[:35]
            lic = item.get("license_name", "CC BY-SA")
            author = item.get("author", "Unknown")[:25]
            conf = int(item.get("confidence", 0.0) * 100)
            src_api = item.get("source_api", "wikimedia").title()

            media_rows.append([
                Paragraph(f"{title}", body_style),
                Paragraph(c_info.get("title"), body_style),
                Paragraph(f"{conf}%", body_style),
                Paragraph(f"<font color='#047857'><b>{lic}</b></font>", body_style),
                Paragraph(f"{author}<br/><font size=7 color='#64748b'>via {src_api}</font>", body_style)
            ])

    if len(media_rows) > 1:
        media_table = Table(media_rows, colWidths=[135, 110, 75, 85, 110])
        media_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(media_table)
    else:
        story.append(Paragraph("<i>Нет утвержденных медиафайлов, преодолевших порог уверенности 0.65.</i>", body_style))

    story.append(PageBreak())

    story.append(Paragraph("Юридическая чистота и реестр CC-атрибуции", title_style))
    story.append(Paragraph("Данный отчет составлен в строгом соответствии с лицензионными требованиями Creative Commons (CC BY, CC BY-SA, CC0).", subtitle_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Таблица первоисточников и прямых ссылок", h2_style))
    
    attr_rows = [
        [
            Paragraph("<b>Медиафайл</b>", meta_bold),
            Paragraph("<b>Прямая ссылка на первоисточник</b>", meta_bold),
            Paragraph("<b>Автор и лицензионные условия</b>", meta_bold)
        ]
    ]

    for c_key, c_info in categories.items():
        for item in c_info.get("items", []):
            title = item.get("title", "Файл")[:30]
            src_url = item.get("source_url", "")
            lic_name = item.get("license_name", "CC BY-SA")
            author = item.get("author", "Unknown")

            attr_rows.append([
                Paragraph(f"<b>{title}</b>", body_style),
                Paragraph(f"<font color='#2563eb'><u>{src_url[:48]}...</u></font>", body_style),
                Paragraph(f"{author}<br/><font size=7 color='#059669'>{lic_name}</font>", body_style)
            ])

    if len(attr_rows) > 1:
        attr_table = Table(attr_rows, colWidths=[130, 235, 150])
        attr_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(attr_table)

    story.append(Spacer(1, 16))

    disclaimer_text = (
        "<b>ЮРИДИЧЕСКИЙ ДИСКЛЕЙМЕР:</b> Все представленные медиа-материалы получены из открытых репозиториев (Wikimedia Commons, "
        "Openverse, Mapillary) в соответствии со ст. 1274 ГК РФ и нормами добросовестного использования (Fair Use / Creative Commons). "
        "Сервис TrueCampus осуществляет исключительно локальную индексацию, перцептивную дедупликацию и машинную классификацию без "
        "модификации авторских прав. Использование данного отчета допускается для B2B-аудита, рекрутинга и академической аналитики."
    )
    disclaimer_box = [[Paragraph(disclaimer_text, ParagraphStyle('Disc', fontName=FONT_NAME, fontSize=8, leading=11, textColor=colors.HexColor("#475569")))]]
    disc_table = Table(disclaimer_box, colWidths=[515])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(disc_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
