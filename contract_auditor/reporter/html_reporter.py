"""HTML报告生成器"""

import os
from datetime import datetime
from jinja2 import Template
from typing import List, Dict
from ..detectors.base_detector import Issue
from ..analyzer.call_graph import CallGraphAnalyzer
from ..analyzer.taint_analysis import TaintAnalyzer


class HTMLReporter:
    """HTML报告生成器"""
    
    def __init__(self):
        self.template_path = os.path.join(
            os.path.dirname(__file__), 
            'templates', 
            'report_template.html'
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

