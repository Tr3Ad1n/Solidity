"""JSON报告生成器"""

import json
from typing import List, Dict
from ..detectors.base_detector import Issue
from ..analyzer.call_graph import CallGraphAnalyzer
from ..analyzer.taint_analysis import TaintAnalyzer


class JSONReporter:
    """JSON报告生成器"""
    
    def __init__(self):
        pass
    
    def generate(self, issues: List[Issue], call_graph: Dict = None, 
                 taint_paths: List = None, control_flow: Dict = None,
                 data_flow: Dict = None, output_path: str = "report.json"):
        """
        生成JSON报告
        
        Args:
            issues: 漏洞列表
            call_graph: 调用图数据
            taint_paths: 污点分析路径
            output_path: 输出文件路径
        """
        report = {
            "summary": self._generate_summary(issues),
            "issues": [issue.to_dict() for issue in issues],
            "analysis": {}
        }
        
        # 添加调用图
        if call_graph:
            report["analysis"]["call_graph"] = call_graph
        
        # 添加污点分析
        if taint_paths:
            analyzer = TaintAnalyzer()
            report["analysis"]["taint_paths"] = analyzer.to_dict(taint_paths)
        
        # 添加控制流分析
        if control_flow:
            report["analysis"]["control_flow"] = {
                func_name: {
                    "nodes": len(cfg.nodes),
                    "edges": len(cfg.edges)
                }
                for func_name, cfg in control_flow.items()
            }
        
        # 添加数据流分析
        if data_flow:
            report["analysis"]["data_flow"] = data_flow
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    
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

