#!/usr/bin/env python3
"""
Simple HTML to PDF Converter - No External Dependencies
Just for testing HTML parsing and structure analysis
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

try:
    # Try to import BeautifulSoup
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("⚠️  BeautifulSoup not available. Using simple HTML parsing.")

@dataclass
class SimpleCard:
    """Simple card structure for analysis"""
    title: str
    content: str
    card_index: int
    has_code: bool = False
    code_content: str = ""
    html_snippet: str = ""

class SimpleHTMLAnalyzer:
    """Simple HTML analyzer to understand card structure"""
    
    def __init__(self):
        self.cards = []
    
    def extract_cards_simple(self, html_file: str) -> tuple[str, List[SimpleCard]]:
        """Extract cards using simple string parsing"""
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        main_title = title_match.group(1) if title_match else Path(html_file).stem
        
        # Find card divs
        card_pattern = r'<div[^>]*class="card"[^>]*>(.*?)</div>\s*</div>'
        card_matches = re.findall(card_pattern, content, re.DOTALL | re.IGNORECASE)
        
        cards = []
        for idx, card_html in enumerate(card_matches):
            # Extract title
            title_match = re.search(r'<h[2-3][^>]*>(.*?)</h[2-3]>', card_html, re.IGNORECASE)
            title = f"Card {idx + 1}"
            if title_match:
                title = re.sub(r'<.*?>', '', title_match.group(1)).strip()
                title = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\-]', '', title).strip()
            
            # Extract content (paragraphs and lists)
            content_parts = []
            p_matches = re.findall(r'<p[^>]*>(.*?)</p>', card_html, re.DOTALL | re.IGNORECASE)
            for p in p_matches:
                clean_p = re.sub(r'<.*?>', '', p).strip()
                if clean_p and not any(keyword in clean_p.lower() for keyword in ['code', 'script']):
                    content_parts.append(clean_p)
            
            # Extract code
            code_matches = re.findall(r'<(?:pre|code)[^>]*>(.*?)</(?:pre|code)>', card_html, re.DOTALL | re.IGNORECASE)
            code_content = '\n'.join(re.sub(r'<.*?>', '', code) for code in code_matches)
            
            # Check for code cards
            has_code_card = 'code-card' in card_html.lower()
            if has_code_card:
                code_card_match = re.search(r'<div[^>]*class="[^"]*code-card[^"]*"[^>]*>(.*?)</div>', card_html, re.DOTALL | re.IGNORECASE)
                if code_card_match:
                    code_content += '\n' + re.sub(r'<.*?>', '', code_card_match.group(1)).strip()
            
            card = SimpleCard(
                title=title,
                content='\n'.join(content_parts),
                card_index=idx,
                has_code=bool(code_content.strip()),
                code_content=code_content.strip(),
                html_snippet=card_html[:200] + "..." if len(card_html) > 200 else card_html
            )
            
            cards.append(card)
        
        return main_title, cards
    
    def extract_cards_bs4(self, html_file: str) -> tuple[str, List[SimpleCard]]:
        """Extract cards using BeautifulSoup"""
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract main title
        title_elem = soup.find('title')
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
                    title = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\-\(\)]', '', title).strip()
                    break
            
            # Extract content
            content_text = ""
            for p in card_elem.find_all(['p', 'li']):
                if not any(cls in (p.get('class', []) or []) for cls in ['code-card', 'code']):
                    text = p.get_text(strip=True)
                    if text:
                        content_text += text + "\n"
            
            # Extract code
            code_elements = card_elem.find_all(['div', 'pre', 'code'], class_=['code-card', 'code'])
            code_content = ""
            for code_elem in code_elements:
                code_content += code_elem.get_text(strip=True) + "\n"
            
            card = SimpleCard(
                title=title,
                content=content_text.strip(),
                card_index=idx,
                has_code=bool(code_content.strip()),
                code_content=code_content.strip(),
                html_snippet=str(card_elem)[:200] + "..."
            )
            
            cards.append(card)
        
        return main_title, cards
    
    def analyze_html_file(self, html_file: str) -> Dict:
        """Analyze HTML file and return structure info"""
        if not os.path.exists(html_file):
            return {"error": f"File not found: {html_file}"}
        
        try:
            if HAS_BS4:
                main_title, cards = self.extract_cards_bs4(html_file)
                parser_used = "BeautifulSoup"
            else:
                main_title, cards = self.extract_cards_simple(html_file)
                parser_used = "Simple RegEx"
            
            return {
                "file": html_file,
                "parser": parser_used,
                "main_title": main_title,
                "total_cards": len(cards),
                "cards": cards,
                "success": True
            }
            
        except Exception as e:
            return {
                "file": html_file,
                "error": str(e),
                "success": False
            }

def print_analysis(analysis: Dict):
    """Print analysis results in a nice format"""
    if not analysis.get("success"):
        print(f"❌ Error analyzing {analysis.get('file', 'unknown')}: {analysis.get('error')}")
        return
    
    print(f"📄 File: {analysis['file']}")
    print(f"🧠 Parser: {analysis['parser']}")
    print(f"📝 Title: {analysis['main_title']}")
    print(f"🃏 Total Cards: {analysis['total_cards']}")
    print("-" * 60)
    
    for card in analysis['cards']:
        print(f"\n📋 Card {card.card_index + 1}: {card.title}")
        print(f"   📝 Content: {len(card.content)} characters")
        print(f"   💻 Has Code: {'Yes' if card.has_code else 'No'}")
        if card.has_code:
            print(f"   📊 Code Length: {len(card.code_content)} characters")
        
        # Show first few lines of content
        if card.content:
            lines = card.content.split('\n')[:2]
            for line in lines:
                if line.strip():
                    preview = line[:80] + "..." if len(line) > 80 else line
                    print(f"      {preview}")
    
    print("\n" + "=" * 60)

def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("🔍 Simple HTML Analyzer")
        print("\nUsage:")
        print("  python simple_html_converter.py <html_file>")
        print("  python simple_html_converter.py --analyze <directory>")
        print("\nExamples:")
        print("  python simple_html_converter.py 'explain/4.1 reflection_pattern_explained.html'")
        print("  python simple_html_converter.py --analyze explain")
        return
    
    analyzer = SimpleHTMLAnalyzer()
    
    if sys.argv[1] == "--analyze":
        # Analyze directory
        directory = sys.argv[2] if len(sys.argv) > 2 else "explain"
        
        if not os.path.exists(directory):
            print(f"❌ Directory not found: {directory}")
            return
        
        html_files = list(Path(directory).glob("*.html"))
        print(f"🔍 Found {len(html_files)} HTML files in {directory}")
        
        for html_file in html_files[:5]:  # Limit to first 5
            print(f"\n{'='*80}")
            analysis = analyzer.analyze_html_file(str(html_file))
            print_analysis(analysis)
    
    else:
        # Analyze single file
        html_file = sys.argv[1]
        analysis = analyzer.analyze_html_file(html_file)
        print_analysis(analysis)

if __name__ == "__main__":
    main()
