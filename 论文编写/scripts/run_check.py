# -*- coding: utf-8 -*-
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

def run_full_check(docx_path):
    output_dir = os.path.join(os.path.dirname(docx_path), 'screenshots')
    
    print('=' * 60)
    print('  论文写作Skill - 完整自检流水线')
    print('=' * 60)
    print('文件: %s' % os.path.basename(docx_path))
    print()
    
    from self_check import run_self_check
    passed, total, results = run_self_check(docx_path)
    
    if passed < total:
        print('\n⚠️  代码自检未全部通过，建议先修复再生成截图')
        user_input = input('\n是否继续生成PDF截图? (y/n): ')
        if user_input.strip().lower() != 'y':
            return passed, total, None, []
    
    try:
        from screenshot_real import full_pipeline
        pdf_path, screenshots = full_pipeline(docx_path, output_dir)
        return passed, total, pdf_path, screenshots
    except Exception as e:
        print('\n截图失败: %s' % e)
        print('提示: 确保已安装 LibreOffice (winget install TheDocumentFoundation.LibreOffice)')
        print('      和 PyMuPDF (pip install PyMuPDF)')
        return passed, total, None, []


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not target:
        import glob
        parent = os.path.dirname(script_dir)
        candidates = glob.glob(os.path.join(parent, '*终稿*.docx'))
        candidates = sorted(candidates, reverse=True)
        target = candidates[0] if candidates else None
    
    if not target or not os.path.exists(target):
        print('用法: python run_check.py <论文.docx路径>')
        sys.exit(1)
    
    run_full_check(target)
