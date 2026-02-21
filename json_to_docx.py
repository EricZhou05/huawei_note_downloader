# -*- coding: utf-8 -*-
import json
import os
import re
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_font(run, font_name, size, bold=False, italic=False):
    """设置字体、字号、加粗、斜体以及中文字体支持"""
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(0, 0, 0)

def add_horizontal_line(paragraph):
    """为段落添加一条粗实线下划线作为分割线"""
    p = paragraph._element
    pPr = p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12')  # 线条粗细
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '000000')
    pBdr.append(bottom)
    pPr.append(pBdr)

def json_to_docx(json_path, output_path):
    # 检查输入文件是否存在
    if not os.path.exists(json_path):
        print(f"错误: 找不到文件 {json_path}")
        return

    # 加载 JSON 数据
    with open(json_path, 'r', encoding='utf-8') as f:
        notes = json.load(f)

    # 创建一个新的 Word 文档
    doc = Document()

    for index, note in enumerate(notes):
        content_raw = note.get('content', '')
        title_raw = note.get('title') or '无标题'
        
        # 1. 标题处理
        # 禁止换行：替换换行符为空格
        title = title_raw.replace('\n', ' ').replace('\r', ' ').strip()
        
        # 标题长度优化：校验 content 前 10 位
        # 先对 content 做简单清理以便比较
        clean_content = content_raw.strip()
        if len(title) >= 10 and len(clean_content) >= 10:
            if title[:10] == clean_content[:10]:
                title = title[:8]
        
        title_para = doc.add_paragraph()
        title_run = title_para.add_run(title)
        set_font(title_run, '微软雅黑', 16, bold=True)
        title_para.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # 2. 添加时间信息
        created_time = note.get('created_time', '未知')
        modified_time = note.get('modified_time', '未知')
        time_info = f"创建时间: {created_time}  |  修改时间: {modified_time}"
        
        time_para = doc.add_paragraph()
        time_run = time_para.add_run(time_info)
        set_font(time_run, '微软雅黑', 9)
        
        # 3. 正文内容处理
        if content_raw:
            # 格式化：压缩冗余换行（多个换行替换为单个）
            content = re.sub(r'\n+', '\n', content_raw).strip()
            
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    content_para = doc.add_paragraph()
                    content_run = content_para.add_run(line)
                    set_font(content_run, '宋体', 11)
                else:
                    doc.add_paragraph()
        else:
            content_para = doc.add_paragraph()
            content_run = content_para.add_run("[无内容]")
            set_font(content_run, '宋体', 11, italic=True)

        # 4. 笔记之间的分割线
        if index < len(notes) - 1:
            # 添加一个空行并带上下划线边框，形成一条明显的分割线
            sep_para = doc.add_paragraph()
            add_horizontal_line(sep_para)
            # 再补一个空行增加间距
            doc.add_paragraph()

    # 保存文档
    doc.save(output_path)
    print(f"转换完成！优化后的 Word 文档已保存至: {output_path}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_json = os.path.join(current_dir, "华为备忘录导出.json")
    output_docx = os.path.join(current_dir, "华为备忘录导出.docx")
    
    json_to_docx(input_json, output_docx)
