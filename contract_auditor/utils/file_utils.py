"""文件处理工具"""

import os
from pathlib import Path
from typing import List, Tuple


def find_solidity_files(path: str) -> List[Tuple[str, str]]:
    """
    查找所有Solidity文件
    
    Args:
        path: 文件或目录路径
        
    Returns:
        List of (file_path, content) tuples
    """
    files = []
    path_obj = Path(path)
    
    if path_obj.is_file():
        if path_obj.suffix == '.sol':
            with open(path_obj, 'r', encoding='utf-8') as f:
                files.append((str(path_obj), f.read()))
    elif path_obj.is_dir():
        for sol_file in path_obj.rglob('*.sol'):
            with open(sol_file, 'r', encoding='utf-8') as f:
                files.append((str(sol_file), f.read()))
    
    return files


def get_output_directory(input_path: str, output_dir: str = None) -> str:
    """
    确定输出目录
    
    Args:
        input_path: 输入文件或目录路径
        output_dir: 用户指定的输出目录
        
    Returns:
        输出目录路径
    """
    from datetime import datetime
    
    if output_dir:
        output_path = Path(output_dir)
    else:
        input_path_obj = Path(input_path)
        if input_path_obj.is_file():
            # 单文件：在合约文件同目录创建audit_report_时间戳
            output_path = input_path_obj.parent / f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            # 项目：在项目根目录创建audit_reports/时间戳
            output_path = input_path_obj / "audit_reports" / datetime.now().strftime('%Y%m%d_%H%M%S')
    
    output_path.mkdir(parents=True, exist_ok=True)
    return str(output_path)

