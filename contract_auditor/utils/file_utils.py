"""文件处理工具"""

import os
from pathlib import Path
from typing import List, Tuple, Dict


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


def classify_files(files: List[Tuple[str, str]], base_path: str = None) -> Dict[str, List[Tuple[str, str]]]:
    """
    分类文件：区分单文件和项目文件
    
    判断规则：
    - 项目：文件在contracts/src/solidity等目录下，或目录下有多个.sol文件且目录名是项目目录
    - 单文件：文件直接在根目录下，或不在项目目录中
    
    Args:
        files: 文件列表 (file_path, content)
        base_path: 基础路径，用于判断项目目录
        
    Returns:
        Dict with 'single_files' and 'projects' keys
    """
    single_files = []
    projects = []
    
    # 常见的项目目录名
    project_dir_names = {'contracts', 'src', 'solidity', 'contract', 'contracts'}
    
    # 统计每个目录下的.sol文件数量
    dir_file_count = {}
    for file_path, _ in files:
        file_obj = Path(file_path)
        parent_dir = str(file_obj.parent)
        
        if parent_dir not in dir_file_count:
            dir_file_count[parent_dir] = 0
        dir_file_count[parent_dir] += 1
    
    # 判断项目目录
    project_dirs = set()
    for dir_path, count in dir_file_count.items():
        dir_name = Path(dir_path).name.lower()
        
        # 规则1: 目录名是常见的项目目录名
        if dir_name in project_dir_names:
            project_dirs.add(dir_path)
        # 规则2: 目录下有多个文件，且目录名看起来像项目目录
        elif count > 1 and (dir_name in project_dir_names or 'contract' in dir_name.lower()):
            project_dirs.add(dir_path)
    
    # 分类文件
    for file_path, content in files:
        file_obj = Path(file_path)
        parent_dir = str(file_obj.parent)
        parent_name = file_obj.parent.name.lower()
        
        # 检查文件是否属于项目目录
        is_project_file = False
        
        # 检查父目录是否是项目目录
        if parent_dir in project_dirs:
            is_project_file = True
        # 检查父目录名是否是项目目录名
        elif parent_name in project_dir_names:
            is_project_file = True
        # 检查是否在项目目录的子目录中
        else:
            for proj_dir in project_dirs:
                if parent_dir.startswith(proj_dir + os.sep) or parent_dir == proj_dir:
                    is_project_file = True
                    break
        
        if is_project_file:
            projects.append((file_path, content))
        else:
            single_files.append((file_path, content))
    
    return {
        'single_files': single_files,
        'projects': projects
    }


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

