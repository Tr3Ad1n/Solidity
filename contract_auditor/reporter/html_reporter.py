"""HTML报告生成器"""

import os
from pathlib import Path
from datetime import datetime
from jinja2 import Template
from typing import List, Dict
from ..detectors.base_detector import Issue
from ..analyzer.call_graph import CallGraphAnalyzer
from ..analyzer.taint_analysis import TaintAnalyzer

try:
    # Python 3.9+ 使用 importlib.resources
    from importlib.resources import files, as_file
    USE_IMPORTLIB = True
except ImportError:
    # Python 3.8 或更早版本使用 pkg_resources
    try:
        import pkg_resources
        USE_IMPORTLIB = False
    except ImportError:
        USE_IMPORTLIB = None

# 对于 Python 3.7-3.8，尝试使用 importlib_resources (backport)
if USE_IMPORTLIB is None:
    try:
        import importlib_resources
        USE_IMPORTLIB = 'backport'
    except ImportError:
        USE_IMPORTLIB = None


class HTMLReporter:
    """HTML报告生成器"""
    
    def __init__(self):
        self.template_path = self._find_template()
    
    def _find_template(self) -> str:
        """查找模板文件，支持多种环境"""
        # 方法1: 尝试使用 importlib.resources (推荐，Python 3.9+)
        if USE_IMPORTLIB is True:
            try:
                template_ref = files('contract_auditor.reporter.templates').joinpath('report_template.html')
                if template_ref.is_file():
                    with as_file(template_ref) as template_path:
                        return str(template_path)
            except (ImportError, FileNotFoundError, ModuleNotFoundError, AttributeError):
                pass
        
        # 方法1b: 尝试使用 importlib_resources (backport for Python 3.7-3.8)
        if USE_IMPORTLIB == 'backport':
            try:
                import importlib_resources
                template_ref = importlib_resources.files('contract_auditor.reporter.templates').joinpath('report_template.html')
                if template_ref.is_file():
                    with importlib_resources.as_file(template_ref) as template_path:
                        return str(template_path)
            except (ImportError, FileNotFoundError, ModuleNotFoundError, AttributeError):
                pass
        
        # 方法2: 尝试使用 pkg_resources (Python 3.8)
        if USE_IMPORTLIB is False:
            try:
                template_path = pkg_resources.resource_filename(
                    'contract_auditor.reporter.templates',
                    'report_template.html'
                )
                if os.path.exists(template_path):
                    return template_path
            except (ImportError, FileNotFoundError, ModuleNotFoundError):
                pass
        
        # 方法3: 使用文件系统路径查找（开发环境）
        current_file = Path(__file__).resolve()
        template_file = current_file.parent / 'templates' / 'report_template.html'
        
        if template_file.exists():
            return str(template_file)
        
        # 方法4: 尝试其他可能的路径
        possible_paths = [
            Path.cwd() / 'contract_auditor' / 'reporter' / 'templates' / 'report_template.html',
            current_file.parent.parent.parent / 'contract_auditor' / 'reporter' / 'templates' / 'report_template.html',
            Path(__file__).parent / 'templates' / 'report_template.html',
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        # 方法5: 最后尝试相对路径
        fallback_path = os.path.join(os.path.dirname(__file__), 'templates', 'report_template.html')
        if os.path.exists(fallback_path):
            return fallback_path
        
        # 所有方法都失败
        raise FileNotFoundError(
            f"HTML模板文件未找到。\n"
            f"当前文件位置: {Path(__file__).resolve()}\n"
            f"请确保 templates/report_template.html 文件存在并被包含在包中。\n"
            f"检查: .gitignore 是否忽略了模板文件，setup.py 是否正确配置了 package_data"
        )
    
    def generate(self, issues: List[Issue], call_graph: Dict = None, 
                 taint_paths: List = None, control_flow: Dict = None,
                 data_flow: Dict = None, output_path: str = "report.html"):
        """
        生成HTML报告
        
        Args:
            issues: 漏洞列表
            call_graph: 调用图数据
            taint_paths: 污点分析路径
            output_path: 输出文件路径
        """
        # 读取模板
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        template = Template(template_content)
        
        # 生成摘要
        summary = self._generate_summary(issues)
        
        # 转换调用图
        call_graph_data = None
        if call_graph:
            call_graph_data = call_graph
        
        # 转换污点路径
        taint_paths_data = None
        if taint_paths:
            analyzer = TaintAnalyzer()
            taint_paths_data = analyzer.to_dict(taint_paths)
        
        # 转换控制流数据
        control_flow_summary = None
        if control_flow:
            control_flow_summary = {
                func_name: {
                    "nodes": len(cfg.nodes),
                    "edges": len(cfg.edges)
                }
                for func_name, cfg in control_flow.items()
            }
        
        # 渲染模板
        html_content = template.render(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            summary=summary,
            issues=[issue.to_dict() for issue in issues],
            call_graph=call_graph_data,
            taint_paths=taint_paths_data,
            control_flow=control_flow_summary,
            data_flow=data_flow
        )
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_summary(self, issues: List[Issue]) -> Dict:
        """生成摘要"""
        from ..utils.severity import Severity
        
        summary = {
            "total_issues": len(issues),
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for issue in issues:
            if issue.severity == Severity.CRITICAL:
                summary["critical"] += 1
            elif issue.severity == Severity.HIGH:
                summary["high"] += 1
            elif issue.severity == Severity.MEDIUM:
                summary["medium"] += 1
            elif issue.severity == Severity.LOW:
                summary["low"] += 1
        
        return summary

