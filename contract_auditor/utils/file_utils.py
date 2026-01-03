"""文件处理工具"""

import os
from pathlib import Path
from typing import List, Tuple, Dict, Any


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


def classify_files(files: List[Tuple[str, str]], base_path: str = None) -> Dict[str, Any]:
    """
    分类文件：区分单文件和项目文件，支持多项目
    
    判断规则：
    - 项目容器目录：目录名是 'project' 或 'projects'，其下的子目录被视为项目
    - 项目目录：在项目容器目录下的文件夹，或 contracts/src/solidity 等目录
    - 单文件：不在任何项目目录中的文件
    
    Args:
        files: 文件列表 (file_path, content)
        base_path: 基础路径，用于判断项目目录
        
    Returns:
        Dict with 'single_files' and 'projects' keys
        'projects' 是一个字典，key 是项目名，value 是该项目的文件列表
    """
    single_files = []
    projects = {}  # 改为字典，key 是项目名，value 是该项目的文件列表
    
    # 项目容器目录名（包含这些名称的目录下的文件夹被视为项目）
    project_container_names = {'project', 'projects'}
    
    # 常见的项目目录名（用于传统项目结构）
    project_dir_names = {'contracts', 'src', 'solidity', 'contract'}
    
    # 第一步：识别项目容器目录（如 examples/project/）
    project_containers = set()
    for file_path, _ in files:
        path_parts = Path(file_path).parts
        for i, part in enumerate(path_parts):
            if part.lower() in project_container_names:
                # 找到项目容器，记录其路径
                container_path = str(Path(*path_parts[:i+1]))
                project_containers.add(container_path)
    
    # 第二步：识别项目目录和项目名
    # 统计每个目录下的文件数
    dir_file_count = {}
    for file_path, _ in files:
        file_obj = Path(file_path)
        parent_dir = str(file_obj.parent)
        if parent_dir not in dir_file_count:
            dir_file_count[parent_dir] = 0
        dir_file_count[parent_dir] += 1
    
    # 建立目录到项目名的映射
    dir_to_project = {}  # key: 目录路径, value: 项目名
    
    for dir_path, count in dir_file_count.items():
        dir_name = Path(dir_path).name.lower()
        path_parts = Path(dir_path).parts
        
        # 检查是否在项目容器目录下
        is_in_container = False
        project_name = None
        
        for container in project_containers:
            container_parts = Path(container).parts
            # 检查目录是否在容器目录下（至少是容器的直接子目录）
            if len(path_parts) > len(container_parts):
                # 检查路径是否以容器路径开头
                if str(dir_path).startswith(container + os.sep) or dir_path == container:
                    is_in_container = True
                    # 项目名是容器目录下的第一层目录名
                    if len(path_parts) > len(container_parts):
                        project_name = path_parts[len(container_parts)]
                    else:
                        project_name = Path(container).name
                    break
        
        # 规则1: 在项目容器目录下
        if is_in_container and project_name:
            dir_to_project[dir_path] = project_name
            # 同时标记所有子目录属于同一项目
            for other_dir in dir_file_count.keys():
                if other_dir != dir_path and (other_dir.startswith(dir_path + os.sep) or other_dir == dir_path):
                    dir_to_project[other_dir] = project_name
        # 规则2: 目录名是常见的项目目录名（传统项目结构）
        elif dir_name in project_dir_names:
            # 尝试从路径推断项目名
            if len(path_parts) > 1:
                # 项目名是父目录名
                project_name = path_parts[-2] if len(path_parts) >= 2 else dir_name
            else:
                project_name = dir_name
            dir_to_project[dir_path] = project_name
        # 规则3: 目录下有多个文件，且目录名看起来像项目目录
        elif count > 1 and (dir_name in project_dir_names or 'contract' in dir_name.lower()):
            if len(path_parts) > 1:
                project_name = path_parts[-2] if len(path_parts) >= 2 else dir_name
            else:
                project_name = dir_name
            dir_to_project[dir_path] = project_name
    
    # 第三步：分类文件
    for file_path, content in files:
        file_obj = Path(file_path)
        parent_dir = str(file_obj.parent)
        parent_name = file_obj.parent.name.lower()
        
        is_project_file = False
        project_name = None
        
        # 检查1: 父目录是否在项目目录映射中
        if parent_dir in dir_to_project:
            is_project_file = True
            project_name = dir_to_project[parent_dir]
        # 检查2: 父目录名是否是项目目录名（传统项目结构）
        elif parent_name in project_dir_names:
            is_project_file = True
            # 尝试从路径推断项目名
            path_parts = Path(parent_dir).parts
            if len(path_parts) > 1:
                project_name = path_parts[-2] if len(path_parts) >= 2 else parent_name
            else:
                project_name = parent_name
        # 检查3: 是否在项目目录的子目录中
        else:
            for proj_dir, proj_name in dir_to_project.items():
                if parent_dir.startswith(proj_dir + os.sep) or parent_dir == proj_dir:
                    is_project_file = True
                    project_name = proj_name
                    break
        
        if is_project_file and project_name:
            if project_name not in projects:
                projects[project_name] = []
            projects[project_name].append((file_path, content))
        else:
            single_files.append((file_path, content))
    
    return {
        'single_files': single_files,
        'projects': projects  # 现在是字典
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

