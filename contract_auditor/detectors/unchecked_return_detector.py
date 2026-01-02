"""未检查返回值检测器"""

from typing import List
from .base_detector import BaseDetector, Issue
from ..parser.ast_builder import AST, FunctionNode, CallNode
from ..utils.severity import Severity


class UncheckedReturnDetector(BaseDetector):
    """检测未检查返回值"""
    
    def detect(self, ast: AST) -> List[Issue]:
        """检测未检查返回值问题"""
        issues = []
        
        for contract in ast.contracts:
            for func in contract.functions:
                # 查找可能失败的调用
                risky_calls = [c for c in func.calls if self._is_risky_call(c)]
                
                for call in risky_calls:
                    if not self._is_return_checked(func, call):
                        issues.append(Issue(
                            issue_type="Unchecked Return Value",
                            severity=Severity.MEDIUM,
                            file_path=ast.file_path,
                            line=call.line,
                            function=func.name,
                            description=f"函数 {func.name} 中的 {call.call_type} 调用未检查返回值，调用可能失败但代码继续执行。",
                            recommendation="检查调用返回值，特别是 send() 和低级别 call() 的返回值，使用 require 确保调用成功。"
                        ))
        
        return issues
    
    def _is_risky_call(self, call: CallNode) -> bool:
        """判断是否是可能失败的调用"""
        risky_types = ['send', 'call', 'delegatecall', 'staticcall']
        return call.call_type in risky_types
    
    def _is_return_checked(self, func: FunctionNode, call: CallNode) -> bool:
        """检查返回值是否被检查"""
        call_line = call.line
        body_after_call = self._get_code_after_line(func.body, call_line)
        
        if not body_after_call:
            return False
        
        import re
        # 检查返回值检查模式
        patterns = [
            r'require\s*\([^)]*\)',
            r'if\s*\([^)]*\)',
            r'assert\s*\(',
            r'\(bool\s+success',
            r'if\s*\(!\s*\w+\)'
        ]
        
        for pattern in patterns:
            if re.search(pattern, body_after_call, re.IGNORECASE):
                return True
        
        return False
    
    def _get_code_after_line(self, body: str, line: int) -> str:
        """获取指定行之后的代码"""
        lines = body.split('\n')
        if line <= len(lines):
            return '\n'.join(lines[line-1:])
        return ""

