"""delegatecall风险检测器"""

from typing import List
from .base_detector import BaseDetector, Issue
from ..parser.ast_builder import AST, FunctionNode, CallNode
from ..utils.severity import Severity


class DelegatecallDetector(BaseDetector):
    """检测危险的delegatecall使用"""
    
    def detect(self, ast: AST) -> List[Issue]:
        """检测delegatecall风险"""
        issues = []
        
        for contract in ast.contracts:
            for func in contract.functions:
                # 查找delegatecall
                delegatecalls = [c for c in func.calls if c.call_type == 'delegatecall']
                
                for call in delegatecalls:
                    # delegatecall总是危险的，需要特别小心
                    is_controlled = self._is_user_controlled(func, call)
                    
                    if is_controlled:
                        issues.append(Issue(
                            issue_type="Dangerous Delegatecall",
                            severity=Severity.CRITICAL,
                            file_path=ast.file_path,
                            line=call.line,
                            function=func.name,
                            description=f"函数 {func.name} 中的 delegatecall 目标可能被用户控制，存在严重安全风险。delegatecall 会使用当前合约的存储执行外部代码。",
                            recommendation="避免使用 delegatecall，或确保目标地址完全可信且不可被用户控制。考虑使用普通 call 或库模式。"
                        ))
                    else:
                        issues.append(Issue(
                            issue_type="Delegatecall Usage",
                            severity=Severity.HIGH,
                            file_path=ast.file_path,
                            line=call.line,
                            function=func.name,
                            description=f"函数 {func.name} 使用了 delegatecall，需要确保目标合约的存储布局与当前合约兼容。",
                            recommendation="仔细审查 delegatecall 的使用，确保目标合约安全且存储布局兼容。考虑使用普通 call 替代。"
                        ))
        
        return issues
    
    def _is_user_controlled(self, func: FunctionNode, call: CallNode) -> bool:
        """检查delegatecall目标是否可能被用户控制"""
        # 简化：检查是否是函数参数或状态变量
        # 如果delegatecall的目标来自msg.sender、函数参数或可修改的状态变量，认为是用户控制的
        
        import re
        
        # 检查函数参数
        for param in func.parameters:
            if 'address' in param.lower() or 'contract' in param.lower():
                # 检查函数体中是否使用该参数作为delegatecall目标
                if re.search(rf'\b{param}\s*\.\s*delegatecall', func.body, re.IGNORECASE):
                    return True
        
        # 检查是否使用msg.sender
        if re.search(r'msg\.sender.*delegatecall', func.body, re.IGNORECASE):
            return True
        
        # 检查是否使用状态变量（可能是可修改的）
        if re.search(r'\w+\[.*\]\s*\.\s*delegatecall', func.body, re.IGNORECASE):
            return True
        
        return False

