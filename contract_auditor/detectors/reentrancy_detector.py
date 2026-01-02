"""重入攻击检测器"""

from typing import List
from .base_detector import BaseDetector, Issue
from ..parser.ast_builder import AST, FunctionNode, CallNode, StateChangeNode
from ..utils.severity import Severity


class ReentrancyDetector(BaseDetector):
    """检测重入攻击风险"""
    
    def detect(self, ast: AST) -> List[Issue]:
        """检测重入风险"""
        issues = []
        
        for contract in ast.contracts:
            for func in contract.functions:
                # 检查是否有外部调用
                external_calls = [c for c in func.calls if self._is_external_call(c)]
                
                if not external_calls:
                    continue
                
                # 检查外部调用后是否有状态修改
                for call in external_calls:
                    # 查找调用后的状态修改
                    state_changes_after = self._find_state_changes_after_call(
                        func, call, external_calls
                    )
                    
                    if state_changes_after:
                        # 检查是否有重入保护
                        has_reentrancy_guard = self._has_reentrancy_guard(func, contract)
                        
                        if not has_reentrancy_guard:
                            issues.append(Issue(
                                issue_type="Reentrancy",
                                severity=Severity.HIGH,
                                file_path=ast.file_path,
                                line=call.line,
                                function=func.name,
                                description=f"函数 {func.name} 在外部调用后修改状态，存在重入攻击风险。外部调用在 {call.line} 行，状态修改在 {[s.line for s in state_changes_after]} 行。",
                                recommendation="使用 Checks-Effects-Interactions 模式，先修改状态再执行外部调用，或使用 ReentrancyGuard 修饰符。"
                            ))
        
        return issues
    
    def _is_external_call(self, call: CallNode) -> bool:
        """判断是否是外部调用"""
        external_call_types = ['call', 'send', 'transfer', 'delegatecall', 'staticcall']
        return call.call_type in external_call_types or call.is_low_level
    
    def _find_state_changes_after_call(self, func: FunctionNode, call: CallNode, 
                                       all_calls: List[CallNode]) -> List[StateChangeNode]:
        """查找调用后的状态修改"""
        changes_after = []
        call_index = func.calls.index(call) if call in func.calls else -1
        
        # 简化：查找调用行号之后的状态修改
        for change in func.state_changes:
            if change.line > call.line:
                changes_after.append(change)
        
        return changes_after
    
    def _has_reentrancy_guard(self, func: FunctionNode, contract) -> bool:
        """检查是否有重入保护"""
        # 检查修饰符
        guard_modifiers = ['nonReentrant', 'reentrancyGuard', 'nonReentrantLock']
        for mod in func.modifiers:
            if mod in guard_modifiers:
                return True
        
        # 检查函数体中是否有锁机制
        if 'nonReentrant' in func.body or 'ReentrancyGuard' in func.body:
            return True
        
        return False

