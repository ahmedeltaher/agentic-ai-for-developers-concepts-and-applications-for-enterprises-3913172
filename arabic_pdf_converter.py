#!/usr/bin/env python3
"""
Enhanced HTML to PDF Converter with Arabic Support
Uses alternative approach for proper Arabic text rendering
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

try:
    import weasyprint
    from weasyprint import HTML, CSS
    print("Using WeasyPrint for better Arabic support")
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("WeasyPrint not available, using alternative method")

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import inch, cm
    from reportlab.lib.colors import Color, blue, black, red, green
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not available")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("BeautifulSoup not available")

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
    print("Arabic reshaper and bidi available")
except ImportError:
    ARABIC_SUPPORT = False
    print("Arabic support libraries not available")


@dataclass
class PDFCard:
    """Card information for PDF generation"""
    title: str
    content: str
    card_index: int
    page_number: int
    bookmark_title: str
    has_code: bool = False
    code_content: str = ""


class ArabicPDFConverter:
    """
    PDF converter with proper Arabic support using multiple methods
    """
    
    def __init__(self, page_size: Tuple = A4):
        self.page_size = page_size
        self.width, self.height = page_size
        self.margin = 2 * cm
        self.content_width = self.width - 2 * self.margin
        self.content_height = self.height - 2 * self.margin
        
        # Try to setup Arabic fonts
        self._setup_arabic_fonts()
    
    def _setup_arabic_fonts(self):
        """Setup Arabic fonts"""
        self.arabic_font = None
        
        # Common Arabic font paths
        font_paths = [
            # macOS
            '/System/Library/Fonts/Arial Unicode.ttf',
            '/Library/Fonts/Arial Unicode.ttf',
            '/System/Library/Fonts/Arial.ttf',
            '/Library/Fonts/Arial.ttf',
            # Linux
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            # Windows
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/calibri.ttf',
        ]
        
        if REPORTLAB_AVAILABLE:
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
                        self.arabic_font = 'ArabicFont'
                        print(f"Registered Arabic font: {font_path}")
                        break
                except Exception as e:
                    continue
            
            if not self.arabic_font:
                self.arabic_font = 'Helvetica'
                print("Using fallback font: Helvetica")
    
    def _process_arabic_text(self, text: str) -> str:
        """Process Arabic text for proper display"""
        if not ARABIC_SUPPORT:
            return text
        
        try:
            # Remove HTML tags
            clean_text = re.sub(r'<[^>]+>', '', text)
            
            # Reshape Arabic text
            reshaped_text = arabic_reshaper.reshape(clean_text)
            
            # Apply bidirectional algorithm
            bidi_text = get_display(reshaped_text)
            
            return bidi_text
        except Exception as e:
            print(f"Arabic processing error: {e}")
            return text
    
    def extract_cards_from_html(self, html_file: str) -> Tuple[str, List[PDFCard]]:
        """Extract cards from HTML file"""
        if not BS4_AVAILABLE:
            print("BeautifulSoup not available, cannot extract cards")
            return "", []
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract main title
        title_elem = soup.find('h1')
        main_title = title_elem.get_text(strip=True) if title_elem else Path(html_file).stem
        main_title = self._process_arabic_text(main_title)
        
        # Find cards
        card_elements = soup.find_all('div', class_='card')
        cards = []
        
        for idx, card_elem in enumerate(card_elements):
            # Extract card title
            title_elem = card_elem.find('h2')
            if title_elem:
                # Remove icon span if exists
                icon_span = title_elem.find('span', class_='icon')
                if icon_span:
                    icon_span.decompose()
                title = title_elem.get_text(strip=True)
            else:
                title = f"البطاقة {idx + 1}"
            
            # Extract content
            content_parts = []
            for p in card_elem.find_all('p'):
                content_parts.append(p.get_text(strip=True))
            
            for ul in card_elem.find_all('ul'):
                for li in ul.find_all('li'):
                    content_parts.append(f"• {li.get_text(strip=True)}")
            
            content_text = '\n'.join(content_parts)
            
            # Check for code
            has_code = False
            code_content = ""
            code_elem = card_elem.find('pre') or card_elem.find('code')
            if code_elem:
                has_code = True
                code_content = code_elem.get_text(strip=True)
            
            # Process Arabic text
            title = self._process_arabic_text(title)
            content_text = self._process_arabic_text(content_text)
            
            card = PDFCard(
                title=title,
                content=content_text,
                card_index=idx,
                page_number=idx + 2,  # +1 for TOC, +1 for 1-based indexing
                bookmark_title=title,
                has_code=has_code,
                code_content=code_content
            )
            cards.append(card)
        
        return main_title, cards
    
    def create_enhanced_html_template(self, main_title: str, cards: List[PDFCard]) -> str:
        """Create enhanced HTML template with proper Arabic support"""
        
        html_template = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;600;700&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Noto Sans Arabic', 'Arial Unicode MS', Arial, sans-serif;
            line-height: 1.8;
            direction: rtl;
            unicode-bidi: bidi-override;
        }}
        
        .page {{
            width: 210mm;
            min-height: 297mm;
            padding: 20mm;
            margin: 0 auto;
            background: white;
            page-break-after: always;
        }}
        
        .page:last-child {{
            page-break-after: auto;
        }}
        
        .toc-page {{
            text-align: center;
        }}
        
        .main-title {{
            font-size: 24pt;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 30mm;
            text-align: center;
        }}
        
        .toc-title {{
            font-size: 18pt;
            font-weight: 600;
            color: #34495e;
            margin-bottom: 20mm;
        }}
        
        .toc-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8mm;
            padding: 5mm 0;
            border-bottom: 1px dotted #bdc3c7;
        }}
        
        .toc-title-text {{
            font-size: 12pt;
            color: #2c3e50;
        }}
        
        .toc-page-num {{
            font-size: 12pt;
            color: #7f8c8d;
            margin-left: 10mm;
        }}
        
        .card-page {{
            background: white;
        }}
        
        .card-title {{
            font-size: 18pt;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15mm;
            border-bottom: 2px solid #e74c3c;
            padding-bottom: 5mm;
        }}
        
        .card-content {{
            font-size: 11pt;
            color: #555;
            line-height: 1.8;
            text-align: justify;
        }}
        
        .card-content p {{
            margin-bottom: 8mm;
        }}
        
        .card-content ul {{
            margin: 10mm 0;
            padding-right: 20mm;
        }}
        
        .card-content li {{
            margin-bottom: 5mm;
        }}
        
        .code-block {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 10mm;
            margin: 10mm 0;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            direction: ltr;
            text-align: left;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        .navigation {{
            position: fixed;
            bottom: 10mm;
            left: 20mm;
            right: 20mm;
            text-align: center;
            font-size: 10pt;
            color: #7f8c8d;
            border-top: 1px solid #ecf0f1;
            padding-top: 5mm;
        }}
        
        @media print {{
            .page {{
                margin: 0;
                box-shadow: none;
            }}
        }}
        
        @page {{
            size: A4;
            margin: 20mm;
        }}
    </style>
</head>
<body>
    <!-- Table of Contents -->
    <div class="page toc-page">
        <h1 class="main-title">{main_title}</h1>
        <h2 class="toc-title">فهرس المحتويات</h2>
        <div class="toc-content">
"""
        
        # Add TOC items
        for card in cards:
            html_template += f"""
            <div class="toc-item">
                <span class="toc-title-text">{card.title}</span>
                <span class="toc-page-num">{card.page_number}</span>
            </div>
"""
        
        html_template += """
        </div>
    </div>
"""
        
        # Add card pages
        for idx, card in enumerate(cards):
            html_template += f"""
    <!-- Card {idx + 1} -->
    <div class="page card-page">
        <h2 class="card-title">{card.title}</h2>
        <div class="card-content">
"""
            
            # Split content into paragraphs
            paragraphs = card.content.split('\n')
            for para in paragraphs:
                if para.strip():
                    if para.strip().startswith('•'):
                        html_template += f"            <p>{para.strip()}</p>\n"
                    else:
                        html_template += f"            <p>{para.strip()}</p>\n"
            
            # Add code if exists
            if card.has_code and card.code_content:
                html_template += f"""
            <div class="code-block">{card.code_content}</div>
"""
            
            html_template += f"""
        </div>
        <div class="navigation">
            صفحة {card.page_number} من {len(cards) + 1} | {card.title}
        </div>
    </div>
"""
        
        html_template += """
</body>
</html>
"""
        
        return html_template
    
    def convert_with_weasyprint(self, html_file: str, output_file: str) -> bool:
        """Convert using WeasyPrint for better Arabic support"""
        try:
            main_title, cards = self.extract_cards_from_html(html_file)
            
            if not cards:
                print("No cards found in HTML file")
                return False
            
            # Create enhanced HTML
            enhanced_html = self.create_enhanced_html_template(main_title, cards)
            
            # Save temporary HTML file
            temp_html = output_file.replace('.pdf', '_temp.html')
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(enhanced_html)
            
            print(f"Created enhanced HTML: {temp_html}")
            
            # Convert to PDF using WeasyPrint
            HTML(temp_html).write_pdf(output_file)
            
            # Clean up temp file
            # os.remove(temp_html)
            
            print(f"✅ Successfully converted to PDF: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ WeasyPrint conversion failed: {e}")
            return False
    
    def convert_with_reportlab(self, html_file: str, output_file: str) -> bool:
        """Fallback conversion using ReportLab"""
        try:
            main_title, cards = self.extract_cards_from_html(html_file)
            
            if not cards:
                print("No cards found in HTML file")
                return False
            
            # Create PDF with ReportLab
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_RIGHT
            
            doc = SimpleDocTemplate(output_file, pagesize=self.page_size,
                                  rightMargin=2*cm, leftMargin=2*cm,
                                  topMargin=2*cm, bottomMargin=2*cm)
            
            styles = getSampleStyleSheet()
            
            # Arabic styles
            title_style = ParagraphStyle(
                'ArabicTitle',
                parent=styles['Heading1'],
                fontName=self.arabic_font,
                fontSize=18,
                alignment=TA_RIGHT,
                spaceAfter=20
            )
            
            content_style = ParagraphStyle(
                'ArabicContent',
                parent=styles['Normal'],
                fontName=self.arabic_font,
                fontSize=11,
                alignment=TA_RIGHT,
                leading=16
            )
            
            story = []
            
            # Add main title
            story.append(Paragraph(main_title, title_style))
            story.append(Spacer(1, 20))
            
            # Add TOC
            toc_style = ParagraphStyle(
                'TOC',
                parent=styles['Normal'],
                fontName=self.arabic_font,
                fontSize=14,
                alignment=TA_RIGHT
            )
            
            story.append(Paragraph("فهرس المحتويات", toc_style))
            story.append(Spacer(1, 10))
            
            for card in cards:
                toc_item = f"{card.title} ... {card.page_number}"
                story.append(Paragraph(toc_item, content_style))
                story.append(Spacer(1, 5))
            
            story.append(PageBreak())
            
            # Add cards
            for card in cards:
                story.append(Paragraph(card.title, title_style))
                story.append(Spacer(1, 10))
                
                # Split content into paragraphs
                paragraphs = card.content.split('\n')
                for para in paragraphs:
                    if para.strip():
                        story.append(Paragraph(para.strip(), content_style))
                        story.append(Spacer(1, 5))
                
                if card.has_code:
                    code_style = ParagraphStyle(
                        'Code',
                        parent=styles['Code'],
                        fontName='Courier',
                        fontSize=9,
                        alignment=TA_LEFT
                    )
                    story.append(Spacer(1, 10))
                    story.append(Paragraph(card.code_content, code_style))
                
                story.append(PageBreak())
            
            doc.build(story)
            print(f"✅ Successfully converted to PDF: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ ReportLab conversion failed: {e}")
            return False
    
    def convert_to_pdf(self, html_file: str, output_file: str = None) -> bool:
        """Main conversion method"""
        if not output_file:
            output_file = html_file.replace('.html', '_arabic.pdf')
        
        print(f"Converting: {html_file} -> {output_file}")
        
        # Try WeasyPrint first (better Arabic support)
        if WEASYPRINT_AVAILABLE:
            print("Attempting conversion with WeasyPrint...")
            if self.convert_with_weasyprint(html_file, output_file):
                return True
        
        # Fallback to ReportLab
        if REPORTLAB_AVAILABLE:
            print("Attempting conversion with ReportLab...")
            if self.convert_with_reportlab(html_file, output_file):
                return True
        
        print("❌ All conversion methods failed")
        return False


def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("""
Arabic PDF Converter Usage:
    python arabic_pdf_converter.py <html_file> [output_file]
    
Examples:
    python arabic_pdf_converter.py explain/4.1_reflection_pattern_explained.html
    python arabic_pdf_converter.py explain/4.1_reflection_pattern_explained.html output.pdf
        """)
        return
    
    converter = ArabicPDFConverter()
    
    html_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(html_file):
        print(f"❌ File not found: {html_file}")
        return
    
    success = converter.convert_to_pdf(html_file, output_file)
    
    if success:
        print("🎉 Conversion completed successfully!")
    else:
        print("💥 Conversion failed!")


if __name__ == "__main__":
    main()
