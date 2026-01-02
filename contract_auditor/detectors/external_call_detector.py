"""外部调用风险检测器"""

from typing import List
from .base_detector import BaseDetector, Issue
from ..parser.ast_builder import AST, FunctionNode, CallNode
from ..utils.severity import Severity


class ExternalCallDetector(BaseDetector):
    """检测外部调用风险"""
    
    def detect(self, ast: AST) -> List[Issue]:
        """检测外部调用问题"""
        issues = []
        
        for contract in ast.contracts:
            for func in contract.functions:
                # 查找低级别调用
                low_level_calls = [c for c in func.calls if c.is_low_level]
                
                for call in low_level_calls:
                    # 检查返回值是否被检查
                    return_checked = self._is_return_checked(func, call)
                    
                    if not return_checked:
                        issues.append(Issue(
                            issue_type="Unchecked External Call",
                            severity=Severity.HIGH,
                            file_path=ast.file_path,
                            line=call.line,
                            function=func.name,
                            description=f"函数 {func.name} 中的低级别调用（{call.call_type}）未检查返回值，调用可能失败但代码继续执行。",
                            recommendation="检查调用返回值，使用 require 或 if 语句验证调用是否成功。"
                        ))
                    
                    # 检查是否发送了value但目标地址可能不可信
                    if call.value and not self._is_trusted_address(func, call):
                        issues.append(Issue(
                            issue_type="Unsafe External Call",
                            severity=Severity.MEDIUM,
                            file_path=ast.file_path,
                            line=call.line,
                            function=func.name,
                            description=f"函数 {func.name} 向可能不可信的地址发送资金，存在风险。",
                            recommendation="验证目标地址的可靠性，或使用 pull payment 模式。"
                        ))
        
        return issues
    
    def _is_return_checked(self, func: FunctionNode, call: CallNode) -> bool:
        """检查返回值是否被检查"""
        # 查找调用后的代码
        call_line = call.line
        
        # 简化：检查函数体中是否有对返回值的检查
        # 查找 (bool success, ...) = 或 require(...) 模式
        body_after_call = self._get_code_after_line(func.body, call_line)
        
        if not body_after_call:
            return False
        
        # 检查是否有返回值检查模式
        return_check_patterns = [
            r'require\s*\(',
            r'if\s*\([^)]*success',
            r'assert\s*\(',
            r'\(bool\s+success'
        ]
        
        import re
        for pattern in return_check_patterns:
            if re.search(pattern, body_after_call, re.IGNORECASE):
                return True
        
        return False
    
    def _get_code_after_line(self, body: str, line: int) -> str:
        """获取指定行之后的代码"""
        lines = body.split('\n')
        if line <= len(lines):
            return '\n'.join(lines[line-1:])
        return ""
    
    def _is_trusted_address(self, func: FunctionNode, call: CallNode) -> bool:
        """检查目标地址是否可信"""
        # 简化：检查是否是合约内部地址或已知安全地址
        # 实际应该进行更复杂的分析
        return False

