"""主入口和CLI接口"""

import click
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# 支持直接运行和作为模块运行
try:
    from .parser.solidity_parser import SolidityParser
    from .detectors.reentrancy_detector import ReentrancyDetector
    from .detectors.access_control_detector import AccessControlDetector
    from .detectors.external_call_detector import ExternalCallDetector
    from .detectors.unchecked_return_detector import UncheckedReturnDetector
    from .detectors.delegatecall_detector import DelegatecallDetector
    from .analyzer.call_graph import CallGraphAnalyzer
    from .analyzer.taint_analysis import TaintAnalyzer
    from .analyzer.control_flow import ControlFlowAnalyzer
    from .analyzer.data_flow import DataFlowAnalyzer
    from .reporter.json_reporter import JSONReporter
    from .reporter.html_reporter import HTMLReporter
    from .utils.file_utils import find_solidity_files, get_output_directory, classify_files
    from .utils.severity import Severity
except ImportError:
    # 如果相对导入失败，尝试绝对导入（直接运行时）
    import os
    # 添加项目根目录到路径
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from contract_auditor.parser.solidity_parser import SolidityParser
    from contract_auditor.detectors.reentrancy_detector import ReentrancyDetector
    from contract_auditor.detectors.access_control_detector import AccessControlDetector
    from contract_auditor.detectors.external_call_detector import ExternalCallDetector
    from contract_auditor.detectors.unchecked_return_detector import UncheckedReturnDetector
    from contract_auditor.detectors.delegatecall_detector import DelegatecallDetector
    from contract_auditor.analyzer.call_graph import CallGraphAnalyzer
    from contract_auditor.analyzer.taint_analysis import TaintAnalyzer
    from contract_auditor.analyzer.control_flow import ControlFlowAnalyzer
    from contract_auditor.analyzer.data_flow import DataFlowAnalyzer
    from contract_auditor.reporter.json_reporter import JSONReporter
    from contract_auditor.reporter.html_reporter import HTMLReporter
    from contract_auditor.utils.file_utils import find_solidity_files, get_output_directory
    from contract_auditor.utils.severity import Severity

from colorama import init, Fore, Style

# 初始化colorama
init(autoreset=True)


def _process_files(files: List[Tuple[str, str]], parser, detectors, 
                   call_graph_analyzer, taint_analyzer, 
                   control_flow_analyzer, data_flow_analyzer):
    """处理文件列表，返回问题和分析数据"""
    all_issues = []
    all_asts = []
    
    # 解析和检测
    print(Fore.YELLOW + "正在解析合约..." + Style.RESET_ALL)
    for file_path, source_code in files:
        print(f"  解析: {file_path}")
        ast = parser.parse(source_code, file_path)
        all_asts.append(ast)
    
    print(Fore.YELLOW + "正在执行安全检测..." + Style.RESET_ALL)
    for ast in all_asts:
        for detector in detectors:
            issues = detector.detect(ast)
            all_issues.extend(issues)
            if issues:
                print(f"  {detector.name}: 发现 {len(issues)} 个问题")
    
    # 执行分析
    call_graph_data = None
    taint_paths = []
    control_flow_data = {}
    data_flow_data = {}
    
    for ast in all_asts:
        # 调用图分析
        call_graph = call_graph_analyzer.analyze(ast)
        if call_graph_data is None:
            call_graph_data = call_graph_analyzer.to_dict()
        
        # 污点分析
        paths = taint_analyzer.analyze(ast)
        taint_paths.extend(paths)
        
        # 控制流分析
        cfgs = control_flow_analyzer.analyze(ast)
        control_flow_data.update(cfgs)
        
        # 数据流分析
        data_flows = data_flow_analyzer.analyze(ast)
        data_flow_data.update(data_flows)
    
    if call_graph_data:
        print(f"  调用图: {len(call_graph_data.get('nodes', []))} 个节点")
    if taint_paths:
        print(f"  污点分析: 发现 {len(taint_paths)} 条传播路径")
    if control_flow_data:
        print(f"  控制流分析: 分析了 {len(control_flow_data)} 个函数")
    if data_flow_data:
        print(f"  数据流分析: 分析了 {len(data_flow_data)} 个函数")
    
    return all_issues, {
        'call_graph': call_graph_data,
        'taint_paths': taint_paths,
        'control_flow': control_flow_data,
        'data_flow': data_flow_data
    }


def _filter_by_severity(issues: List, severity: str):
    """按风险等级过滤问题"""
    min_severity = Severity.from_string(severity)
    severity_order = {
        Severity.CRITICAL: 4,
        Severity.HIGH: 3,
        Severity.MEDIUM: 2,
        Severity.LOW: 1
    }
    return [
        issue for issue in issues
        if severity_order.get(issue.severity, 0) >= severity_order.get(min_severity, 0)
    ]


@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(), help='输出目录')
@click.option('--format', '-f', type=click.Choice(['json', 'html', 'both'], case_sensitive=False), 
              default='both', help='输出格式')
@click.option('--severity', '-s', type=click.Choice(['critical', 'high', 'medium', 'low'], case_sensitive=False),
              default='low', help='最低风险等级过滤')
def main(input_path, output_dir, format, severity):
    """
    智能合约安全审计工具
    
    扫描 Solidity 智能合约，检测安全漏洞并生成报告。
    
    INPUT_PATH: 要扫描的合约文件或目录路径
    """
    try:
        print(Fore.CYAN + Style.BRIGHT + "\n" + "="*60)
        print("  智能合约安全审计工具")
        print("="*60 + Style.RESET_ALL + "\n")
        
        # 查找Solidity文件
        print(Fore.YELLOW + "正在查找 Solidity 文件..." + Style.RESET_ALL)
        files = find_solidity_files(input_path)
        
        if not files:
            print(Fore.RED + f"错误: 在 {input_path} 中未找到 .sol 文件" + Style.RESET_ALL)
            sys.exit(1)
        
        print(Fore.GREEN + f"找到 {len(files)} 个 Solidity 文件" + Style.RESET_ALL)
        
        # 分类文件：区分单文件和项目
        input_path_obj = Path(input_path)
        is_single_file = input_path_obj.is_file()
        
        if is_single_file:
            # 单文件模式：直接处理
            classified = {'single_files': files, 'projects': []}
        else:
            # 目录模式：分类文件
            classified = classify_files(files, str(input_path_obj))
            print(Fore.CYAN + f"  单文件: {len(classified['single_files'])} 个" + Style.RESET_ALL)
            print(Fore.CYAN + f"  项目文件: {len(classified['projects'])} 个" + Style.RESET_ALL)
        
        # 确定输出目录
        base_output_dir = get_output_directory(input_path, output_dir)
        
        # 判断是否需要分开报告
        has_both = len(classified['single_files']) > 0 and len(classified['projects']) > 0
        
        # 初始化组件
        parser = SolidityParser()
        detectors = [
            ReentrancyDetector(),
            AccessControlDetector(),
            ExternalCallDetector(),
            UncheckedReturnDetector(),
            DelegatecallDetector()
        ]
        
        json_reporter = JSONReporter()
        html_reporter = HTMLReporter()
        
        # 处理单文件和项目，分别生成报告
        reports_generated = []
        filtered_single_issues = []
        filtered_projects_issues = []
        
        # 处理单文件
        if classified['single_files']:
            print(Fore.YELLOW + "\n" + "="*60 + Style.RESET_ALL)
            print(Fore.YELLOW + "处理单文件..." + Style.RESET_ALL)
            
            single_files_issues, single_files_data = _process_files(
                classified['single_files'], parser, detectors,
                call_graph_analyzer=CallGraphAnalyzer(),
                taint_analyzer=TaintAnalyzer(),
                control_flow_analyzer=ControlFlowAnalyzer(),
                data_flow_analyzer=DataFlowAnalyzer()
            )
            
            # 过滤风险等级
            filtered_single_issues = _filter_by_severity(single_files_issues, severity)
            
            # 生成报告
            if has_both:
                # 有单文件和项目，使用子目录
                single_output_dir = Path(base_output_dir) / "single_files"
                single_output_dir.mkdir(parents=True, exist_ok=True)
            else:
                # 只有单文件，使用原输出目录
                single_output_dir = Path(base_output_dir)
            
            if format in ['json', 'both']:
                json_path = str(single_output_dir / "report.json")
                json_reporter.generate(filtered_single_issues, single_files_data['call_graph'],
                                     single_files_data['taint_paths'],
                                     single_files_data['control_flow'],
                                     single_files_data['data_flow'], json_path)
                print(Fore.GREEN + f"  单文件JSON报告: {json_path}" + Style.RESET_ALL)
                reports_generated.append(json_path)
            
            if format in ['html', 'both']:
                html_path = str(single_output_dir / "report.html")
                html_reporter.generate(filtered_single_issues, single_files_data['call_graph'],
                                      single_files_data['taint_paths'],
                                      single_files_data['control_flow'],
                                      single_files_data['data_flow'], html_path)
                print(Fore.GREEN + f"  单文件HTML报告: {html_path}" + Style.RESET_ALL)
                reports_generated.append(html_path)
        
        # 处理项目
        if classified['projects']:
            print(Fore.YELLOW + "\n" + "="*60 + Style.RESET_ALL)
            print(Fore.YELLOW + "处理项目文件..." + Style.RESET_ALL)
            
            projects_issues, projects_data = _process_files(
                classified['projects'], parser, detectors,
                call_graph_analyzer=CallGraphAnalyzer(),
                taint_analyzer=TaintAnalyzer(),
                control_flow_analyzer=ControlFlowAnalyzer(),
                data_flow_analyzer=DataFlowAnalyzer()
            )
            
            # 过滤风险等级
            filtered_projects_issues = _filter_by_severity(projects_issues, severity)
            
            # 生成报告
            if has_both:
                # 有单文件和项目，使用子目录
                projects_output_dir = Path(base_output_dir) / "projects"
                projects_output_dir.mkdir(parents=True, exist_ok=True)
            else:
                # 只有项目，使用原输出目录
                projects_output_dir = Path(base_output_dir)
            
            if format in ['json', 'both']:
                json_path = str(projects_output_dir / "report.json")
                json_reporter.generate(filtered_projects_issues, projects_data['call_graph'],
                                     projects_data['taint_paths'],
                                     projects_data['control_flow'],
                                     projects_data['data_flow'], json_path)
                print(Fore.GREEN + f"  项目JSON报告: {json_path}" + Style.RESET_ALL)
                reports_generated.append(json_path)
            
            if format in ['html', 'both']:
                html_path = str(projects_output_dir / "report.html")
                html_reporter.generate(filtered_projects_issues, projects_data['call_graph'],
                                      projects_data['taint_paths'],
                                      projects_data['control_flow'],
                                      projects_data['data_flow'], html_path)
                print(Fore.GREEN + f"  项目HTML报告: {html_path}" + Style.RESET_ALL)
                reports_generated.append(html_path)
        
        # 显示摘要
        print(Fore.CYAN + Style.BRIGHT + "\n" + "="*60)
        print("  检测完成")
        print("="*60 + Style.RESET_ALL)
        
        from collections import Counter
        
        # 汇总所有问题
        all_filtered_issues = []
        if classified['single_files']:
            all_filtered_issues.extend(filtered_single_issues)
        if classified['projects']:
            all_filtered_issues.extend(filtered_projects_issues)
        
        if all_filtered_issues:
            severity_counts = Counter([str(issue.severity) for issue in all_filtered_issues])
            
            print(f"\n总计发现: {len(all_filtered_issues)} 个问题")
            print(f"  Critical: {severity_counts.get('Critical', 0)}")
            print(f"  High: {severity_counts.get('High', 0)}")
            print(f"  Medium: {severity_counts.get('Medium', 0)}")
            print(f"  Low: {severity_counts.get('Low', 0)}")
            
            if classified['single_files'] and classified['projects']:
                print(f"\n  单文件: {len(filtered_single_issues)} 个问题")
                print(f"  项目: {len(filtered_projects_issues)} 个问题")
        
        print(Fore.GREEN + f"\n报告已保存到: {base_output_dir}" + Style.RESET_ALL)
        if classified['single_files'] and classified['projects']:
            print(Fore.CYAN + f"  单文件报告: {base_output_dir}/single_files/" + Style.RESET_ALL)
            print(Fore.CYAN + f"  项目报告: {base_output_dir}/projects/" + Style.RESET_ALL)
        
        if len(all_filtered_issues) > 0:
            sys.exit(1)  # 有漏洞时返回非0退出码
        else:
            sys.exit(0)
    
    except Exception as e:
        print(Fore.RED + f"\n错误: {str(e)}" + Style.RESET_ALL)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

