#!/usr/bin/env python3
"""
Simple Arabic PDF Converter - Fixed version for Arabic support
"""

import sys
import os
import re
from pathlib import Path

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import cm
    from reportlab.lib.colors import Color
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER
except ImportError:
    print("Error: ReportLab not installed. Install with: pip install reportlab")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: BeautifulSoup not installed. Install with: pip install beautifulsoup4")
    sys.exit(1)

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
    print("✅ Arabic support libraries loaded")
except ImportError:
    ARABIC_SUPPORT = False
    print("⚠️ Arabic support libraries not available, using basic conversion")


class SimpleArabicPDFConverter:
    """Simple PDF converter with Arabic support"""
    
    def __init__(self):
        self.setup_fonts()
    
    def setup_fonts(self):
        """Setup Arabic fonts"""
        self.arabic_font = None
        
        # Try to register Arabic fonts
        font_paths = [
            # macOS
            '/System/Library/Fonts/Arial Unicode.ttf',
            '/Library/Fonts/Arial.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
            # Linux
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            # Windows
            'C:/Windows/Fonts/arial.ttf',
        ]
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
                    self.arabic_font = 'ArabicFont'
                    print(f"✅ Registered font: {font_path}")
                    break
            except Exception as e:
                continue
        
        if not self.arabic_font:
            self.arabic_font = 'Helvetica'
            print("⚠️ Using fallback font: Helvetica")
    
    def process_arabic_text(self, text: str) -> str:
        """Process Arabic text for proper display"""
        if not text:
            return ""
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        if ARABIC_SUPPORT:
            try:
                # Reshape Arabic text
                reshaped_text = arabic_reshaper.reshape(clean_text)
                # Apply bidirectional algorithm
                bidi_text = get_display(reshaped_text)
                return bidi_text
            except Exception as e:
                print(f"Arabic processing error: {e}")
                return clean_text
        
        return clean_text
    
    def extract_content(self, html_file: str):
        """Extract content from HTML file"""
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract title
        title_elem = soup.find('h1')
        main_title = title_elem.get_text(strip=True) if title_elem else "مستند PDF"
        main_title = self.process_arabic_text(main_title)
        
        # Extract cards
        cards = []
        card_elements = soup.find_all('div', class_='card')
        
        for idx, card_elem in enumerate(card_elements):
            # Get card title
            title_elem = card_elem.find('h2')
            if title_elem:
                # Remove icon if exists
                icon = title_elem.find('span', class_='icon')
                if icon:
                    icon.decompose()
                card_title = title_elem.get_text(strip=True)
            else:
                card_title = f"البطاقة {idx + 1}"
            
            # Get card content
            content_parts = []
            
            # Extract paragraphs
            for p in card_elem.find_all('p'):
                text = p.get_text(strip=True)
                if text:
                    content_parts.append(text)
            
            # Extract lists
            for ul in card_elem.find_all('ul'):
                for li in ul.find_all('li'):
                    text = li.get_text(strip=True)
                    if text:
                        content_parts.append(f"• {text}")
            
            # Extract highlights and special sections
            for div in card_elem.find_all('div', class_=['highlight', 'best-practices', 'warning', 'tips']):
                text = div.get_text(strip=True)
                if text and len(text) > 20:  # Avoid short decorative texts
                    content_parts.append(f"📌 {text}")
            
            card_content = '\n\n'.join(content_parts)
            
            # Process Arabic text
            card_title = self.process_arabic_text(card_title)
            card_content = self.process_arabic_text(card_content)
            
            cards.append({
                'title': card_title,
                'content': card_content,
                'index': idx + 1
            })
        
        return main_title, cards
    
    def create_pdf(self, html_file: str, output_file: str = None):
        """Create PDF from HTML file"""
        if not output_file:
            output_file = html_file.replace('.html', '_arabic_fixed.pdf')
        
        print(f"🔄 Converting: {html_file}")
        print(f"📄 Output: {output_file}")
        
        # Extract content
        main_title, cards = self.extract_content(html_file)
        
        if not cards:
            print("❌ No cards found in HTML file")
            return False
        
        print(f"📚 Found {len(cards)} cards")
        
        # Create PDF
        doc = SimpleDocTemplate(
            output_file,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Setup styles
        styles = getSampleStyleSheet()
        
        # Main title style
        title_style = ParagraphStyle(
            'MainTitle',
            parent=styles['Title'],
            fontName=self.arabic_font,
            fontSize=20,
            alignment=TA_CENTER,
            textColor=Color(0.17, 0.24, 0.31),  # Dark blue
            spaceAfter=30,
            spaceBefore=20
        )
        
        # Card title style
        card_title_style = ParagraphStyle(
            'CardTitle',
            parent=styles['Heading1'],
            fontName=self.arabic_font,
            fontSize=16,
            alignment=TA_RIGHT,
            textColor=Color(0.17, 0.24, 0.31),
            spaceAfter=20,
            spaceBefore=10
        )
        
        # Content style
        content_style = ParagraphStyle(
            'Content',
            parent=styles['Normal'],
            fontName=self.arabic_font,
            fontSize=11,
            alignment=TA_RIGHT,
            leading=16,
            spaceAfter=10,
            textColor=Color(0.2, 0.2, 0.2)
        )
        
        # TOC style
        toc_style = ParagraphStyle(
            'TOC',
            parent=styles['Normal'],
            fontName=self.arabic_font,
            fontSize=12,
            alignment=TA_RIGHT,
            leading=18,
            spaceAfter=8
        )
        
        # Build story
        story = []
        
        # Main title
        story.append(Paragraph(main_title, title_style))
        story.append(Spacer(1, 20))
        
        # Table of contents
        toc_title = self.process_arabic_text("فهرس المحتويات")
        story.append(Paragraph(toc_title, card_title_style))
        story.append(Spacer(1, 15))
        
        for idx, card in enumerate(cards):
            toc_entry = f"{card['title']} {'.' * 20} {idx + 2}"
            story.append(Paragraph(toc_entry, toc_style))
        
        story.append(PageBreak())
        
        # Add cards
        for idx, card in enumerate(cards):
            # Card title
            story.append(Paragraph(card['title'], card_title_style))
            
            # Card content
            paragraphs = card['content'].split('\n\n')
            for para in paragraphs:
                if para.strip():
                    # Handle different types of content
                    if para.startswith('📌'):
                        # Highlighted content
                        highlight_style = ParagraphStyle(
                            'Highlight',
                            parent=content_style,
                            backColor=Color(1, 0.98, 0.8),  # Light yellow
                            borderWidth=1,
                            borderColor=Color(0.9, 0.7, 0.1),
                            borderPadding=8
                        )
                        story.append(Paragraph(para, highlight_style))
                    else:
                        story.append(Paragraph(para, content_style))
                    
                    story.append(Spacer(1, 8))
            
            # Page break after each card (except last)
            if idx < len(cards) - 1:
                story.append(PageBreak())
        
        # Build PDF
        try:
            doc.build(story)
            print(f"✅ PDF created successfully: {output_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to create PDF: {e}")
            return False


def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("""
🔄 Simple Arabic PDF Converter

Usage:
    python simple_arabic_converter.py <html_file> [output_file]

Examples:
    python simple_arabic_converter.py 'explain/4.1 reflection_pattern_explained.html'
    python simple_arabic_converter.py 'explain/4.1 reflection_pattern_explained.html' output.pdf

Features:
    ✅ Proper Arabic text support
    ✅ Card-based page layout
    ✅ Table of contents
    ✅ RTL text direction
    ✅ Arabic font handling
        """)
        return
    
    html_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(html_file):
        print(f"❌ File not found: {html_file}")
        return
    
    converter = SimpleArabicPDFConverter()
    success = converter.create_pdf(html_file, output_file)
    
    if success:
        print("🎉 Conversion completed successfully!")
        if output_file:
            print(f"📂 Open: {output_file}")
    else:
        print("💥 Conversion failed!")


if __name__ == "__main__":
    main()
