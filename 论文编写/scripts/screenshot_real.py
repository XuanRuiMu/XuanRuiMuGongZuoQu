# -*- coding: utf-8 -*-
"""
论文截图自检工具 - 接收用户手动转换的PDF
重要：不再使用LibreOffice转换！用户必须使用WPS Office或Word手动输出PDF
"""
import os
import sys

def pdf_to_screenshots(pdf_path, output_dir, dpi=200):
    """将PDF转换为PNG截图用于视觉检查"""
    try:
        import fitz
    except ImportError:
        raise RuntimeError('PyMuPDF未安装! 运行: pip install PyMuPDF')
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f'PDF文件不存在: {pdf_path}')
    
    os.makedirs(output_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    page_count = len(doc)
    file_size_kb = os.path.getsize(pdf_path) / 1024
    
    print('PDF文件: %s' % os.path.basename(pdf_path))
    print('文件大小: %.1f KB' % file_size_kb)
    print('总页数: %d页' % page_count)
    print('截图分辨率: %d dpi' % dpi)
    print('-' * 50)
    
    screenshots = []
    for i in range(page_count):
        page = doc[i]
        pix = page.get_pixmap(dpi=dpi)
        png_name = 'real_page_%02d.png' % (i + 1)
        png_path = os.path.join(output_dir, png_name)
        pix.save(png_path)
        size_kb = os.path.getsize(png_path) / 1024
        screenshots.append(png_path)
        print('  第%2d页 -> %s (%.0f KB) [%dx%d]' % (i+1, png_name, size_kb, pix.width, pix.height))
    
    doc.close()
    return screenshots


def main():
    """
    用法1: python screenshot_real.py <pdf路径>
    用法2: python screenshot_real.py <docx路径> (会提示需要先转PDF)
    """
    if len(sys.argv) < 2:
        print('=' * 60)
        print('论文截图自检工具')
        print('=' * 60)
        print()
        print('用法:')
        print('  python screenshot_real.py <PDF文件路径>')
        print()
        print('注意: 必须先用WPS Office或Word将docx转换为PDF!')
        print('      不要使用LibreOffice转换(格式会出错)')
        print()
        print('推荐转换方法:')
        print('  1. 用WPS Office打开docx文件')
        print('  2. 点击"文件" -> "输出为PDF"')
        print('  3. 保存到论文目录下')
        print()
        sys.exit(1)
    
    target = sys.argv[1]
    
    if not os.path.exists(target):
        print(f'错误: 文件不存在 - {target}')
        sys.exit(1)
    
    # 判断是PDF还是DOCX
    if target.lower().endswith('.docx'):
        pdf_hint = target.replace('.docx', '.pdf')
        print('=' * 60)
        print('⚠️  检测到DOCX文件，需要先转换为PDF')
        print('=' * 60)
        print()
        print(f'DOCX文件: {target}')
        print()
        print('请按以下步骤操作:')
        print(f'  1. 用WPS Office打开: {target}')
        print(f'  2. 点击"文件" -> "输出为PDF"')
        print(f'  3. 保存为: {pdf_hint}')
        print()
        print('完成后运行:')
        print(f'  python screenshot_real.py {pdf_hint}')
        print()
        sys.exit(0)
    
    if not target.lower().endswith('.pdf'):
        print('错误: 只支持PDF文件格式')
        sys.exit(1)
    
    # 处理PDF文件
    output_dir = os.path.join(os.path.dirname(target), 'screenshots')
    
    print('=' * 60)
    print('论文截图自检流水线')
    print('=' * 60)
    print('输入: %s' % target)
    print('输出: %s' % output_dir)
    print()
    
    try:
        screenshots = pdf_to_screenshots(target, output_dir)
        print()
        print('=' * 60)
        print('✓ 完成! 共生成 %d 页截图' % len(screenshots))
        print('  保存在: %s' % output_dir)
        print('=' * 60)
    except Exception as e:
        print()
        print('✗ 错误: %s' % str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
