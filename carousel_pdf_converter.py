#!/usr/bin/env python3
"""
Enhanced HTML to PDF Converter with Advanced Carousel Features
Includes bookmarks, hyperlinks, and interactive navigation
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, 
                                  PageBreak, Table, TableStyle)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
    from reportlab.lib.colors import Color, blue, black, red, green
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
    from reportlab.platypus.frames import Frame
except ImportError:
    print("Error: ReportLab not installed. Install with: pip install reportlab")
    exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: BeautifulSoup not installed. Install with: pip install beautifulsoup4")
    exit(1)


@dataclass
class PDFCard:
    """Enhanced card information for PDF generation"""
    title: str
    content: str
    card_index: int
    page_number: int
    bookmark_title: str
    has_code: bool = False
    code_content: str = ""
    estimated_height: float = 0.0
    

class CarouselPDFConverter:
    """
    Advanced PDF converter with carousel navigation and interactive features
    """
    
    def __init__(self, page_size: Tuple = A4):
        self.page_size = page_size
        self.width, self.height = page_size
        self.margin = 2 * cm
        self.content_width = self.width - 2 * self.margin
        self.content_height = self.height - 2 * self.margin
        
        # Navigation dimensions
        self.nav_height = 1.5 * cm
        self.footer_height = 1 * cm
        
        # Colors
        self.primary_color = Color(0.17, 0.24, 0.31)  # #2c3e50
        self.secondary_color = Color(0.90, 0.30, 0.24)  # #e74c3c
        self.text_color = Color(0.2, 0.2, 0.2)
        self.nav_color = Color(0.0, 0.48, 1.0)  # #007bff
        
        self._setup_fonts()
        self._setup_styles()
        
    def _setup_fonts(self):
        """Setup fonts with fallbacks"""
        self.fonts = {
            'arabic': 'Helvetica',  # Fallback
            'code': 'Courier',
            'default': 'Helvetica'
        }
        
        # Try to register better fonts
        font_candidates = [
            ('/System/Library/Fonts/Arial.ttf', 'Arabic'),
            ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'Arabic'),
            ('C:/Windows/Fonts/arial.ttf', 'Arabic'),
        ]
        
        for font_path, font_name in font_candidates:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    self.fonts['arabic'] = font_name
                    break
                except:
                    continue
    
    def _setup_styles(self):
        """Setup paragraph styles"""
        self.styles = getSampleStyleSheet()
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CardTitle',
            parent=self.styles['Heading1'],
            fontName=self.fonts['arabic'],
            fontSize=18,
            alignment=TA_RIGHT,
            textColor=self.primary_color,
            spaceAfter=20,
            spaceBefore=10
        ))
        
        # Content style
        self.styles.add(ParagraphStyle(
            name='CardContent',
            parent=self.styles['Normal'],
            fontName=self.fonts['arabic'],
            fontSize=11,
            alignment=TA_RIGHT,
            textColor=self.text_color,
            leading=16,
            spaceAfter=10
        ))
        
        # Code style
        self.styles.add(ParagraphStyle(
            name='CodeBlock',
            parent=self.styles['Code'],
            fontName=self.fonts['code'],
            fontSize=9,
            alignment=TA_LEFT,
            textColor=black,
            backColor=Color(0.97, 0.97, 0.97),
            leftIndent=10,
            rightIndent=10,
            borderWidth=1,
            borderColor=Color(0.8, 0.8, 0.8),
            borderPadding=8
        ))
        
        # Navigation style
        self.styles.add(ParagraphStyle(
            name='NavLink',
            parent=self.styles['Normal'],
            fontName=self.fonts['arabic'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=self.nav_color
        ))

    def extract_cards(self, html_file: str) -> Tuple[str, List[PDFCard]]:
        """Extract cards and main title from HTML file"""
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract main title
        title_elem = soup.find('h1')
        main_title = title_elem.get_text(strip=True) if title_elem else Path(html_file).stem
        
        # Find cards
        card_elements = soup.find_all('div', class_='card')
        cards = []
        
        for idx, card_elem in enumerate(card_elements):
            # Extract title
            title_selectors = ['h2', 'h3', '.card-title']
            title = f"Card {idx + 1}"
            
            for selector in title_selectors:
                title_elem = card_elem.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    # Clean title
                    title = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\-\(\)]', '', title).strip()
                    break
            
            # Extract content
            content_text = ""
            for p in card_elem.find_all(['p', 'li']):
                if not any(cls in (p.get('class', []) or []) for cls in ['code-card', 'code']):
                    text = p.get_text(strip=True)
                    if text:
                        content_text += text + "\n\n"
            
            # Extract code
            code_elements = card_elem.find_all(['div', 'pre'], class_=['code-card', 'code'])
            code_content = ""
            for code_elem in code_elements:
                code_content += code_elem.get_text(strip=True) + "\n\n"
            
            # Create bookmark title
            bookmark_title = f"{idx + 1}. {title[:30]}..."
            
            card = PDFCard(
                title=title,
                content=content_text.strip(),
                card_index=idx,
                page_number=idx + 2,  # +2 because of TOC
                bookmark_title=bookmark_title,
                has_code=bool(code_content),
                code_content=code_content.strip()
            )
            
            cards.append(card)
        
        return main_title, cards

    def create_toc_page(self, canvas_obj: Canvas, main_title: str, cards: List[PDFCard]):
        """Create table of contents page"""
        canvas_obj.setFont(self.fonts['arabic'], 24)
        canvas_obj.setFillColor(self.primary_color)
        
        # Main title
        title_width = canvas_obj.stringWidth(main_title, self.fonts['arabic'], 24)
        x_pos = self.width - self.margin - title_width
        canvas_obj.drawString(x_pos, self.height - self.margin - 30, main_title)
        
        # TOC title
        toc_title = "فهرس المحتويات"
        canvas_obj.setFont(self.fonts['arabic'], 18)
        toc_width = canvas_obj.stringWidth(toc_title, self.fonts['arabic'], 18)
        x_pos = self.width - self.margin - toc_width
        canvas_obj.drawString(x_pos, self.height - self.margin - 80, toc_title)
        
        # TOC entries
        canvas_obj.setFont(self.fonts['arabic'], 12)
        canvas_obj.setFillColor(self.text_color)
        
        y_pos = self.height - self.margin - 120
        for card in cards:
            if y_pos < self.margin + 50:  # Not enough space
                break
                
            entry_text = f"{card.card_index + 1}. {card.title}"
            page_text = f"صفحة {card.page_number}"
            
            # Entry title (right aligned)
            entry_width = canvas_obj.stringWidth(entry_text, self.fonts['arabic'], 12)
            canvas_obj.drawString(self.width - self.margin - entry_width, y_pos, entry_text)
            
            # Page number (left aligned)
            canvas_obj.drawString(self.margin, y_pos, page_text)
            
            # Dotted line
            dots_start = self.margin + canvas_obj.stringWidth(page_text, self.fonts['arabic'], 12) + 10
            dots_end = self.width - self.margin - entry_width - 10
            self._draw_dotted_line(canvas_obj, dots_start, dots_end, y_pos + 3)
            
            y_pos -= 25

    def _draw_dotted_line(self, canvas_obj: Canvas, start_x: float, end_x: float, y: float):
        """Draw dotted line for TOC"""
        canvas_obj.setStrokeColor(Color(0.7, 0.7, 0.7))
        canvas_obj.setLineWidth(0.5)
        
        x = start_x
        while x < end_x:
            canvas_obj.line(x, y, min(x + 3, end_x), y)
            x += 6

    def create_card_page(self, canvas_obj: Canvas, card: PDFCard, cards: List[PDFCard]):
        """Create a single card page with navigation"""
        # Card title
        canvas_obj.setFont(self.fonts['arabic'], 18)
        canvas_obj.setFillColor(self.primary_color)
        
        title_width = canvas_obj.stringWidth(card.title, self.fonts['arabic'], 18)
        x_pos = self.width - self.margin - title_width
        canvas_obj.drawString(x_pos, self.height - self.margin - 30, card.title)
        
        # Underline
        canvas_obj.setStrokeColor(self.secondary_color)
        canvas_obj.setLineWidth(2)
        canvas_obj.line(x_pos, self.height - self.margin - 35, 
                       self.width - self.margin, self.height - self.margin - 35)
        
        # Content
        canvas_obj.setFont(self.fonts['arabic'], 11)
        canvas_obj.setFillColor(self.text_color)
        
        y_pos = self.height - self.margin - 70
        
        # Split content into lines
        if card.content:
            lines = self._wrap_text(canvas_obj, card.content, self.content_width - 40, 
                                  self.fonts['arabic'], 11)
            
            for line in lines:
                if y_pos < self.margin + self.nav_height + 50:
                    break
                    
                line_width = canvas_obj.stringWidth(line, self.fonts['arabic'], 11)
                x_pos = self.width - self.margin - line_width
                canvas_obj.drawString(x_pos, y_pos, line)
                y_pos -= 16
        
        # Code section
        if card.has_code and card.code_content and y_pos > self.margin + self.nav_height + 100:
            y_pos -= 20
            
            # Code title
            code_title = "الكود:"
            canvas_obj.setFont(self.fonts['arabic'], 12)
            canvas_obj.setFillColor(self.secondary_color)
            title_width = canvas_obj.stringWidth(code_title, self.fonts['arabic'], 12)
            x_pos = self.width - self.margin - title_width
            canvas_obj.drawString(x_pos, y_pos, code_title)
            
            y_pos -= 25
            
            # Code content
            canvas_obj.setFont(self.fonts['code'], 9)
            canvas_obj.setFillColor(black)
            
            # Background for code
            code_lines = card.code_content.split('\n')[:15]  # Limit lines
            code_height = len(code_lines) * 12 + 20
            
            if y_pos - code_height > self.margin + self.nav_height:
                canvas_obj.setFillColor(Color(0.97, 0.97, 0.97))
                canvas_obj.rect(self.margin, y_pos - code_height + 10, 
                              self.content_width, code_height, fill=1, stroke=0)
                
                canvas_obj.setFillColor(black)
                for line in code_lines:
                    if y_pos < self.margin + self.nav_height + 30:
                        break
                    if line.strip():
                        canvas_obj.drawString(self.margin + 10, y_pos, line[:80])  # Limit width
                    y_pos -= 12
        
        # Navigation
        self._add_navigation(canvas_obj, card, cards)

    def _wrap_text(self, canvas_obj: Canvas, text: str, max_width: float, 
                   font_name: str, font_size: int) -> List[str]:
        """Wrap text to fit within specified width"""
        canvas_obj.setFont(font_name, font_size)
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if canvas_obj.stringWidth(test_line, font_name, font_size) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines

    def _add_navigation(self, canvas_obj: Canvas, current_card: PDFCard, cards: List[PDFCard]):
        """Add navigation elements at bottom of page"""
        nav_y = self.margin + 10
        
        canvas_obj.setFont(self.fonts['arabic'], 10)
        canvas_obj.setFillColor(self.nav_color)
        
        # Page indicator
        page_info = f"الصفحة {current_card.page_number} من {len(cards) + 1}"
        page_width = canvas_obj.stringWidth(page_info, self.fonts['arabic'], 10)
        canvas_obj.drawString((self.width - page_width) / 2, nav_y + 20, page_info)
        
        # Previous button
        if current_card.card_index > 0:
            prev_text = "← السابق"
            canvas_obj.drawString(self.margin, nav_y, prev_text)
        
        # Next button
        if current_card.card_index < len(cards) - 1:
            next_text = "التالي →"
            next_width = canvas_obj.stringWidth(next_text, self.fonts['arabic'], 10)
            canvas_obj.drawString(self.width - self.margin - next_width, nav_y, next_text)
        
        # TOC link
        toc_text = "الفهرس"
        toc_width = canvas_obj.stringWidth(toc_text, self.fonts['arabic'], 10)
        canvas_obj.drawString((self.width - toc_width) / 2, nav_y, toc_text)

    def convert_to_pdf(self, html_file: str, output_file: str) -> bool:
        """Convert HTML file to PDF with carousel navigation"""
        try:
            # Extract data
            main_title, cards = self.extract_cards(html_file)
            
            if not cards:
                print("No cards found in HTML file")
                return False
            
            # Create PDF
            canvas_obj = canvas.Canvas(output_file, pagesize=self.page_size)
            
            # Add metadata
            canvas_obj.setTitle(main_title)
            canvas_obj.setAuthor("HTML to PDF Converter")
            canvas_obj.setSubject("Agentic AI Learning Materials")
            
            # Create TOC page
            self.create_toc_page(canvas_obj, main_title, cards)
            canvas_obj.showPage()
            
            # Create card pages
            for card in cards:
                self.create_card_page(canvas_obj, card, cards)
                canvas_obj.showPage()
            
            # Save PDF
            canvas_obj.save()
            
            print(f"✅ Successfully created PDF: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating PDF: {e}")
            return False

    def batch_convert(self, input_dir: str, output_dir: str) -> Dict[str, bool]:
        """Convert multiple HTML files"""
        results = {}
        
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        html_files = list(input_path.glob("*.html"))
        
        for html_file in html_files:
            pdf_file = output_path / f"{html_file.stem}_carousel.pdf"
            
            print(f"Converting {html_file.name}...")
            success = self.convert_to_pdf(str(html_file), str(pdf_file))
            results[html_file.name] = success
        
        return results


def main():
    """Command line interface for the converter"""
    import sys
    
    if len(sys.argv) < 2:
        print("🚀 HTML to PDF Carousel Converter")
        print("\nUsage:")
        print("  python carousel_pdf_converter.py <html_file> [output_file]")
        print("  python carousel_pdf_converter.py --batch <input_dir> [output_dir]")
        print("\nExamples:")
        print("  # Convert single file")
        print("  python carousel_pdf_converter.py 'explain/4.1 reflection_pattern_explained.html'")
        print("  python carousel_pdf_converter.py 'explain/4.1 reflection_pattern_explained.html' 'output.pdf'")
        print("\n  # Batch convert all HTML files in directory")
        print("  python carousel_pdf_converter.py --batch explain")
        print("  python carousel_pdf_converter.py --batch explain pdfs/")
        print("\n  # Test conversion")
        print("  python carousel_pdf_converter.py --test")
        return
    
    converter = CarouselPDFConverter()
    
    if sys.argv[1] == "--test":
        # Test with example file
        html_file = "explain/4.1 reflection_pattern_explained.html"
        pdf_file = "explain/pdfs/reflection_pattern_carousel.pdf"
        
        if os.path.exists(html_file):
            Path(pdf_file).parent.mkdir(parents=True, exist_ok=True)
            print(f"🧪 Testing with: {html_file}")
            success = converter.convert_to_pdf(html_file, pdf_file)
            
            if success:
                print(f"✅ Test successful!")
                print(f"📄 PDF created: {pdf_file}")
                print(f"📊 File size: {os.path.getsize(pdf_file) / 1024:.1f} KB")
            else:
                print("❌ Test failed!")
        else:
            print(f"❌ Test file not found: {html_file}")
            
    elif sys.argv[1] == "--batch":
        # Batch conversion
        input_dir = sys.argv[2] if len(sys.argv) > 2 else "explain"
        output_dir = sys.argv[3] if len(sys.argv) > 3 else f"{input_dir}/pdfs"
        
        print(f"🔄 Batch converting from: {input_dir}")
        print(f"📁 Output directory: {output_dir}")
        
        results = converter.batch_convert(input_dir, output_dir)
        success_count = sum(1 for success in results.values() if success)
        
        print(f"\n📈 Results: {success_count}/{len(results)} files converted successfully")
        
        for filename, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {filename}")
            
    else:
        # Single file conversion
        html_file = sys.argv[1]
        
        if len(sys.argv) > 2:
            pdf_file = sys.argv[2]
        else:
            # Generate output filename
            base_name = Path(html_file).stem
            pdf_file = f"{base_name}_carousel.pdf"
        
        print(f"🔄 Converting: {html_file}")
        print(f"📄 Output: {pdf_file}")
        
        if not os.path.exists(html_file):
            print(f"❌ Input file not found: {html_file}")
            return
        
        # Create output directory if needed
        Path(pdf_file).parent.mkdir(parents=True, exist_ok=True)
        
        success = converter.convert_to_pdf(html_file, pdf_file)
        
        if success:
            print(f"✅ Conversion successful!")
            print(f"📊 File size: {os.path.getsize(pdf_file) / 1024:.1f} KB")
        else:
            print("❌ Conversion failed!")


if __name__ == "__main__":
    main()
