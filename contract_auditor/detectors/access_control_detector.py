"""权限控制检测器"""

from typing import List
from .base_detector import BaseDetector, Issue
from ..parser.ast_builder import AST, FunctionNode
from ..utils.severity import Severity


class AccessControlDetector(BaseDetector):
    """检测权限控制缺失"""
    
    def detect(self, ast: AST) -> List[Issue]:
        """检测权限控制问题"""
        issues = []
        
        # 关键函数名模式
        critical_functions = [
            'withdraw', 'transfer', 'mint', 'burn', 'pause', 'unpause',
            'setOwner', 'setAdmin', 'upgrade', 'destroy', 'kill', 'selfdestruct'
        ]
        
        for contract in ast.contracts:
            for func in contract.functions:
                # 检查是否是关键函数
                is_critical = any(cf in func.name.lower() for cf in critical_functions)
                
                if not is_critical:
                    # 检查是否修改状态变量
                    if not func.state_changes:
                        continue
                
                # 检查是否有权限控制
                has_access_control = self._has_access_control(func, contract)
                
                if not has_access_control and (is_critical or func.state_changes):
                    # 检查是否是构造函数或view函数
                    if func.name == contract.name or func.is_view or func.is_pure:
                        continue
                    
                    severity = Severity.HIGH if is_critical else Severity.MEDIUM
                    
                    issues.append(Issue(
                        issue_type="Access Control",
                        severity=severity,
                        file_path=ast.file_path,
                        line=func.line,
                        function=func.name,
                        description=f"函数 {func.name} 缺少访问控制修饰符，可能允许未授权访问。",
                        recommendation="添加 onlyOwner、onlyRole 或其他访问控制修饰符，确保只有授权用户可以调用此函数。"
                    ))
        
        return issues
    
    def _has_access_control(self, func: FunctionNode, contract) -> bool:
        """检查是否有访问控制"""
        # 检查修饰符
        access_control_modifiers = [
            'onlyOwner', 'onlyAdmin', 'onlyRole', 'onlyWhitelist',
            'onlyAuthorized', 'hasRole', 'isOwner'
        ]
        
        for mod in func.modifiers:
            if any(acm in mod for acm in access_control_modifiers):
                return True
        
        # 检查函数体中是否有权限检查
        access_control_keywords = ['require', 'assert', 'onlyOwner', 'msg.sender']
        body_lower = func.body.lower()
        
        # 简单检查：如果函数体中有require且涉及msg.sender，可能有权限控制
        if 'require' in body_lower and 'msg.sender' in body_lower:
            return True
        
        return False

