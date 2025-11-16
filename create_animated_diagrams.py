#!/usr/bin/env python3
"""
Enhanced HTML Generator with Animated Diagrams
Converts all diagram types to beautiful animated HTML blocks
"""
import os
import re

# Enhanced CSS with diagram styles
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
        }

        /* Workflow Diagram Styles */
        .workflow-diagram {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 40px 20px;
            margin: 30px 0;
            direction: rtl;
        }

        .workflow-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
            direction: rtl;
        }

        .workflow-step {
            background: white;
            border: 3px solid #667eea;
            border-radius: 12px;
            padding: 20px 30px;
            min-width: 280px;
            max-width: 500px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            animation: fadeInUp 0.6s ease-out forwards;
            opacity: 0;
            position: relative;
            direction: rtl;
        }

        .workflow-step.user { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .workflow-step.orchestrator { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }
        .workflow-step.planner { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }
        .workflow-step.executor { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; }
        .workflow-step.tool { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: #2c3e50; }
        .workflow-step.result { background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); color: white; }
        .workflow-step.llm { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #2c3e50; }
        .workflow-step.index { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #2c3e50; }

        .workflow-arrow {
            font-size: 2rem;
            color: #e67e22;
            animation: bounce 2s infinite;
            margin: 5px 0;
        }

        .workflow-step h3 {
            font-size: 1.2rem;
            margin-bottom: 8px;
            font-weight: bold;
        }

        .workflow-step p {
            font-size: 0.95rem;
            line-height: 1.5;
            margin: 5px 0;
        }

        .step-number {
            position: absolute;
            top: -15px;
            left: -15px;
            background: #e67e22;
            color: white;
            width: 38px;
            height: 38px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.1rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        .loop-indicator {
            background: rgba(230, 126, 34, 0.1);
            border: 3px dashed #e67e22;
            border-radius: 15px;
            padding: 25px 15px;
            margin: 15px 0;
        }

        .parallel-container {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            60% { transform: translateY(-5px); }
        }

        .workflow-step:nth-child(1) { animation-delay: 0.1s; }
        .workflow-step:nth-child(3) { animation-delay: 0.2s; }
        .workflow-step:nth-child(5) { animation-delay: 0.3s; }
        .workflow-step:nth-child(7) { animation-delay: 0.4s; }
        .workflow-step:nth-child(9) { animation-delay: 0.5s; }
        .workflow-step:nth-child(11) { animation-delay: 0.6s; }
        .workflow-step:nth-child(13) { animation-delay: 0.7s; }
        .workflow-step:nth-child(15) { animation-delay: 0.8s; }
        .workflow-step:nth-child(17) { animation-delay: 0.9s; }
        .workflow-step:nth-child(19) { animation-delay: 1.0s; }
        .workflow-step:nth-child(21) { animation-delay: 1.1s; }'''

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

def detect_diagram_type(lines):
    """Detect if lines contain a complex flow diagram (not simple code)"""
    # Must have box characters (ASCII art) forming a structure
    has_boxes = any('┌' in line or '└' in line or '├' in line for line in lines)
    
    # Must have proper box structure (multiple box lines)
    box_lines = [l for l in lines if '┌' in l or '└' in l or '├' in l or '─' in l]
    
    # Must be a LARGE complex diagram (has boxes AND more than 15 lines AND multiple box components)
    is_complex_diagram = has_boxes and len(lines) > 15 and len(box_lines) > 5
    
    # Simple code blocks with arrows or few boxes should stay as code
    if not has_boxes or len(box_lines) <= 5:
        return False
    
    return is_complex_diagram

def convert_to_animated_diagram(lines):
    """Convert text diagram to animated HTML blocks"""
    html = '<div class="workflow-diagram"><div class="workflow-container">\n'
    
    step_num = 1
    for line in lines:
        line = line.strip()
        if not line or line == '```':
            continue
        
        # Detect component type
        comp_type = 'workflow-step'
        if '👤' in line or 'مستخدم' in line or 'User' in line:
            comp_type += ' user'
        elif '🎼' in line or 'Orchestrator' in line or 'منسق' in line:
            comp_type += ' orchestrator'
        elif '📋' in line or 'Planner' in line or 'مخطط' in line:
            comp_type += ' planner'
        elif '⚙️' in line or 'Executor' in line or 'منفذ' in line:
            comp_type += ' executor'
        elif '🛠️' in line or 'Tool' in line or 'أداة' in line:
            comp_type += ' tool'
        elif '🧠' in line or 'LLM' in line:
            comp_type += ' llm'
        elif '📊' in line or '📤' in line or 'نتيجة' in line or 'Result' in line:
            comp_type += ' result'
        elif '💾' in line or 'Index' in line or 'فهرس' in line:
            comp_type += ' index'
        
        # Check if arrow
        if line in ['↓', '⬇️', '→', '⬅️', '←']:
            html += '<div class="workflow-arrow">⬇️</div>\n'
        elif '→' in line or '↓' in line or '⬇️' in line:
            # Step with content
            clean_line = line.replace('│', '').replace('┌', '').replace('└', '').replace('├', '').replace('─', '').strip()
            if clean_line and not clean_line.startswith('('):
                html += f'<div class="{comp_type}"><div class="step-number">{step_num}</div><h3>{process_text(clean_line)}</h3></div>\n'
                html += '<div class="workflow-arrow">⬇️</div>\n'
                step_num += 1
    
    html += '</div></div>'
    return html

def parse_markdown(content):
    """Parse markdown and create card structure with diagram detection"""
    content = content.replace('<div dir="rtl">', '').replace('</div>', '').strip()
    lines = content.split('\n')
    
    main_title = ''
    cards = []
    current_card = None
    current_subcard = None
    in_code = False
    code_buffer = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Handle code blocks
        if line.strip().startswith('```'):
            if not in_code:
                in_code = True
                code_buffer = []
            else:
                in_code = False
                # Check if diagram
                if detect_diagram_type(code_buffer):
                    diagram_html = convert_to_animated_diagram(code_buffer)
                    if current_subcard:
                        current_subcard['content'] += diagram_html + '\n'
                    elif current_card:
                        current_card['content'] += diagram_html + '\n'
                else:
                    # Regular code block
                    code_html = '\n'.join(code_buffer)
                    if current_subcard:
                        current_subcard['content'] += f'<div class="code-card"><pre>{code_html}</pre></div>\n'
                    elif current_card:
                        current_card['content'] += f'<div class="code-card"><pre>{code_html}</pre></div>\n'
                code_buffer = []
            i += 1
            continue
        
        if in_code:
            code_buffer.append(line)
            i += 1
            continue
        
        # Main title
        if line.startswith('# ') and not line.startswith('##'):
            main_title = process_text(line[2:].strip())
            i += 1
            continue
        
        # Card titles
        if (line.startswith('## ') or line.startswith('### ')) and not line.startswith('####'):
            if current_subcard and current_card:
                current_card['subcards'].append(current_subcard)
                current_subcard = None
            if current_card:
                cards.append(current_card)
            
            title = process_text(line.replace('###', '').replace('##', '').strip())
            current_card = {'title': title, 'content': '', 'subcards': []}
            i += 1
            continue
        
        # Subcard titles
        if line.startswith('#### '):
            if current_subcard and current_card:
                current_card['subcards'].append(current_subcard)
            title = process_text(line[5:].strip())
            current_subcard = {'title': title, 'content': ''}
            i += 1
            continue
        
        # Add content
        if current_subcard:
            current_subcard['content'] += line + '\n'
        elif current_card:
            current_card['content'] += line + '\n'
        
        i += 1
    
    if current_subcard and current_card:
        current_card['subcards'].append(current_subcard)
    if current_card:
        cards.append(current_card)
    
    return main_title, cards

def content_to_html(content):
    """Convert content to HTML"""
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
        
        # Skip already processed elements
        if s.startswith('<div class'):
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(s)
            continue
        
        # Tables
        if '|' in s:
            table_buffer.append(s)
            continue
        else:
            if table_buffer:
                result.append(create_table(table_buffer))
                table_buffer = []
        
        # Lists
        if s.startswith('- '):
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(f'<li>{process_text(s[2:])}</li>')
            continue
        
        # Blockquotes
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

print("🚀 بدء إنشاء ملفات HTML مع Animated Diagrams...\n")

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

print('\n🎉 تم إنشاء جميع الملفات بنجاح مع Animated Diagrams!')
print('📁 الملفات في: explain/')
print('🎨 جميع الـ diagrams الآن متحركة وبصرية!')
