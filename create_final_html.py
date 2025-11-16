#!/usr/bin/env python3
"""
Complete HTML Generator matching 3.5 style exactly
Creates 16 HTML files from markdown with Egyptian Arabic explanations
"""
import os
import re

CSS = '''        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            direction: rtl;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }

        .card-title {
            color: #2c3e50;
            font-size: 1.8rem;
            margin-bottom: 20px;
            border-bottom: 3px solid #e67e22;
            padding-bottom: 10px;
        }

        .card-content {
            line-height: 1.8;
            color: #333;
            font-size: 1.1rem;
        }

        .process-step {
            background: #f8f9fa;
            border-left: 5px solid #e67e22;
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 10px 10px 0;
        }

        .process-step h4 {
            color: #e67e22;
            margin-bottom: 10px;
        }

        .code-card {
            background: #2c3e50;
            color: #ecf0f1;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            direction: ltr;
            text-align: left;
        }

        .code-card pre {
            overflow-x: auto;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }

        th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: center;
        }

        td {
            padding: 15px;
            border: 1px solid #ddd;
            text-align: center;
        }

        tr:nth-child(even) {
            background: #f8f9ff;
        }

        ul, ol {
            margin: 15px 0;
            padding-right: 30px;
        }

        li {
            margin: 10px 0;
        }

        code {
            background: #f0f4ff;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }

        strong {
            color: #2c3e50;
        }

        blockquote {
            background: #e8f5e8;
            border-right: 4px solid #27ae60;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 5px;
        }'''

def process_text(text):
    """Process inline markdown"""
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text

def create_table(lines):
    """Convert markdown table to HTML"""
    if len(lines) < 2:
        return ''
    
    html = '<table>\n'
    for i, line in enumerate(lines):
        if re.match(r'^[\s\|:\-]+$', line):
            continue
        cells = [process_text(c.strip()) for c in line.split('|') if c.strip()]
        if not cells:
            continue
        if i == 0 or i == 1:
            html += '<tr>' + ''.join([f'<th>{c}</th>' for c in cells]) + '</tr>\n'
        else:
            html += '<tr>' + ''.join([f'<td>{c}</td>' for c in cells]) + '</tr>\n'
    html += '</table>'
    return html

def parse_markdown(content):
    """Parse markdown and create card structure"""
    content = content.replace('<div dir="rtl">', '').replace('</div>', '').strip()
    lines = content.split('\n')
    
    main_title = ''
    cards = []
    current_card = None
    current_subcard = None
    in_code = False
    code_buffer = []
    
    for line in lines:
        # Handle code blocks
        if line.strip().startswith('```'):
            if not in_code:
                in_code = True
                code_buffer = []
            else:
                in_code = False
                code_html = '\n'.join(code_buffer)
                if current_subcard:
                    current_subcard['content'] += f'<div class="code-card"><pre>{code_html}</pre></div>\n'
                elif current_card:
                    current_card['content'] += f'<div class="code-card"><pre>{code_html}</pre></div>\n'
                code_buffer = []
            continue
        
        if in_code:
            code_buffer.append(line)
            continue
        
        # Main title (single #)
        if line.startswith('# ') and not line.startswith('##'):
            main_title = process_text(line[2:].strip())
            continue
        
        # Card titles (## or ###)
        if (line.startswith('## ') or line.startswith('### ')) and not line.startswith('####'):
            # Save previous subcard
            if current_subcard and current_card:
                current_card['subcards'].append(current_subcard)
                current_subcard = None
            # Save previous card
            if current_card:
                cards.append(current_card)
            
            title = process_text(line.replace('###', '').replace('##', '').strip())
            current_card = {'title': title, 'content': '', 'subcards': []}
            continue
        
        # Subcard titles (####)
        if line.startswith('#### '):
            if current_subcard and current_card:
                current_card['subcards'].append(current_subcard)
            title = process_text(line[5:].strip())
            current_subcard = {'title': title, 'content': ''}
            continue
        
        # Add content to appropriate container
        if current_subcard:
            current_subcard['content'] += line + '\n'
        elif current_card:
            current_card['content'] += line + '\n'
    
    # Save final items
    if current_subcard and current_card:
        current_card['subcards'].append(current_subcard)
    if current_card:
        cards.append(current_card)
    
    return main_title, cards

def content_to_html(content):
    """Convert content to HTML with proper formatting"""
    if not content.strip():
        return ''
    
    lines = content.split('\n')
    result = []
    in_list = False
    table_buffer = []
    
    for line in lines:
        s = line.strip()
        
        if not s:
            if in_list:
                result.append('</ul>')
                in_list = False
            continue
        
        # Skip already processed divs
        if s.startswith('<div class'):
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(s)
            continue
        
        # Handle tables
        if '|' in s:
            table_buffer.append(s)
            continue
        else:
            if table_buffer:
                result.append(create_table(table_buffer))
                table_buffer = []
        
        # Handle lists
        if s.startswith('- '):
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(f'<li>{process_text(s[2:])}</li>')
            continue
        
        # Handle blockquotes
        if s.startswith('> '):
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(f'<blockquote>{process_text(s[2:])}</blockquote>')
            continue
        
        # Regular paragraphs
        if in_list:
            result.append('</ul>')
            in_list = False
        
        if s and not s.startswith('---'):
            result.append(f'<p>{process_text(s)}</p>')
    
    if in_list:
        result.append('</ul>')
    if table_buffer:
        result.append(create_table(table_buffer))
    
    return '\n'.join(result)

def create_html_file(main_title, cards, page_title):
    """Generate complete HTML file"""
    if not main_title:
        main_title = page_title
    
    cards_html = ''
    for card in cards:
        if not card['title']:
            continue
        
        card_html = f'''
        <div class="card">
            <h2 class="card-title">{card['title']}</h2>
            <div class="card-content">
                {content_to_html(card['content'])}
'''
        
        # Add subcards as process-steps
        for subcard in card.get('subcards', []):
            if subcard['title']:
                card_html += f'''
                <div class="process-step">
                    <h4>{subcard['title']}</h4>
                    {content_to_html(subcard['content'])}
                </div>
'''
        
        card_html += '''
            </div>
        </div>
'''
        cards_html += card_html
    
    return f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <style>
{CSS}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 {main_title}</h1>
            <p>شرح مفصل بالعامية المصرية</p>
        </div>
{cards_html}
    </div>
</body>
</html>'''

# File mappings
files = {
    '1.1': 'الذكاء الاصطناعي التوليدي الأساسي',
    '1.2': 'إيه هو الـ Agentic AI؟',
    '1.3': 'مثال على الـ Agentic AI',
    '1.4': 'فوائد وتحديات الـ Agentic AI',
    '1.5': 'التقنيات المستخدمة في الـ Agentic AI',
    '2.1': 'مكونات نظام الـ Agentic AI',
    '2.2': 'الأهداف في الـ Agentic AI',
    '2.3': 'المخطط (Planner) في الـ Agentic AI',
    '2.4': 'المنسق والمنفذ في الـ Agentic AI',
    '2.5': 'الأدوات في الـ Agentic AI',
    '2.6': 'نماذج الذكاء الاصطناعي التوليدي',
    '2.7': 'Memory في Agentic AI',
    '3.1': 'بناء AI Agent بسيط',
    '3.2': 'تصميم Router AI Agent',
    '3.3': 'إعداد الـ Indexes للـ Router',
    '3.4': 'إعداد الـ Agentic Router'
}

print("🚀 بدء إنشاء ملفات HTML...\n")

for num, title in files.items():
    md_file = f'explain/mark_down/{num}.md'
    html_file = f'explain/{num}_explained.html'
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        main_title, cards = parse_markdown(md_content)
        html = create_html_file(main_title, cards, title)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        subcards_count = sum(len(c.get('subcards', [])) for c in cards)
        print(f'✅ {num}_explained.html - {len(cards)} cards, {subcards_count} subcards')
    except Exception as e:
        print(f'❌ {num}: {str(e)}')

print('\n🎉 تم إنشاء جميع الملفات بنجاح!')
print('📁 الملفات في: explain/*.html')
