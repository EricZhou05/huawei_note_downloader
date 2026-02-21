# -*- coding: utf-8 -*-
import json
import os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

def set_font(run, font_name, size, bold=False, italic=False):
    """设置字体、字号、加粗、斜体以及中文字体支持"""
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(0, 0, 0)

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
        # 1. 添加标题 - 使用微软雅黑，16号加粗
        title = note.get('title') or '无标题'
        title_para = doc.add_paragraph()
        title_run = title_para.add_run(title)
        set_font(title_run, '微软雅黑', 16, bold=True)
        title_para.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # 2. 添加时间信息 - 使用微软雅黑，9号
        created_time = note.get('created_time', '未知')
        modified_time = note.get('modified_time', '未知')
        time_info = f"创建时间: {created_time}  |  修改时间: {modified_time}"
        
        time_para = doc.add_paragraph()
        time_run = time_para.add_run(time_info)
        set_font(time_run, '微软雅黑', 9)
        
        # 3. 添加正文内容 - 使用宋体，11号
        content = note.get('content', '')
        if content:
            # 华为备忘录通常有很多换行，这里逐行处理以保持段落感
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    content_para = doc.add_paragraph()
                    content_run = content_para.add_run(line)
                    set_font(content_run, '宋体', 11)
                else:
                    # 空行处理
                    doc.add_paragraph()
        else:
            content_para = doc.add_paragraph()
            content_run = content_para.add_run("[无内容]")
            set_font(content_run, '宋体', 11, italic=True)

        # 4. 在笔记之间添加分隔（除了最后一个）
        if index < len(notes) - 1:
            sep_para = doc.add_paragraph()
            sep_run = sep_para.add_run("-" * 50)
            set_font(sep_run, 'Calibri', 10)
            sep_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 保存文档
    doc.save(output_path)
    print(f"转换完成！Word 文档已保存至: {output_path}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_json = os.path.join(current_dir, "华为备忘录导出.json")
    output_docx = os.path.join(current_dir, "华为备忘录导出.docx")
    
    json_to_docx(input_json, output_docx)
