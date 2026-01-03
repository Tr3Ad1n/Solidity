"""HTML报告生成器"""

import os
from pathlib import Path
from datetime import datetime
from jinja2 import Template
from typing import List, Dict
from ..detectors.base_detector import Issue
from ..analyzer.call_graph import CallGraphAnalyzer
from ..analyzer.taint_analysis import TaintAnalyzer


class HTMLReporter:
    """HTML报告生成器"""
    
    def __init__(self):
        # 使用绝对路径，确保在CI环境中也能找到模板
        current_file = Path(__file__).resolve()
        template_file = current_file.parent / 'templates' / 'report_template.html'
        
        # 如果找不到，尝试多个可能的路径
        if not template_file.exists():
            # 尝试从项目根目录查找
            possible_paths = [
                Path.cwd() / 'contract_auditor' / 'reporter' / 'templates' / 'report_template.html',
                current_file.parent.parent.parent / 'contract_auditor' / 'reporter' / 'templates' / 'report_template.html',
                # 在CI环境中，可能是从site-packages安装的
                Path(__file__).parent / 'templates' / 'report_template.html',
            ]
            
            for path in possible_paths:
                if path.exists():
                    template_file = path
                    break
        
        self.template_path = str(template_file)
        
        # 验证模板文件是否存在
        if not Path(self.template_path).exists():
            # 如果还是找不到，尝试使用相对路径（作为最后手段）
            fallback_path = os.path.join(os.path.dirname(__file__), 'templates', 'report_template.html')
            if os.path.exists(fallback_path):
                self.template_path = fallback_path
            else:
                raise FileNotFoundError(
                    f"HTML模板文件未找到。尝试的路径:\n"
                    f"  - {template_file}\n"
                    f"  - {fallback_path}\n"
                    f"当前文件位置: {current_file}\n"
                    f"请确保 templates/report_template.html 文件存在"
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

