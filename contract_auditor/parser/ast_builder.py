"""AST节点定义"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class ASTNode:
    """AST节点基类"""
    line: int
    column: int = 0


@dataclass
class ContractNode(ASTNode):
    """合约节点"""
    name: str = ""
    functions: List['FunctionNode'] = field(default_factory=list)
    state_variables: List['StateVariableNode'] = field(default_factory=list)
    modifiers: List['ModifierNode'] = field(default_factory=list)


@dataclass
class FunctionNode(ASTNode):
    """函数节点"""
    name: str = ""
    visibility: str = "public"  # public, private, internal, external
    modifiers: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    returns: List[str] = field(default_factory=list)
    body: str = ""
    is_payable: bool = False
    is_view: bool = False
    is_pure: bool = False
    calls: List['CallNode'] = field(default_factory=list)
    state_changes: List['StateChangeNode'] = field(default_factory=list)


@dataclass
class ModifierNode(ASTNode):
    """修饰符节点"""
    name: str = ""
    body: str = ""


@dataclass
class StateVariableNode(ASTNode):
    """状态变量节点"""
    name: str = ""
    var_type: str = ""
    visibility: str = "internal"
    is_constant: bool = False


@dataclass
class CallNode(ASTNode):
    """调用节点"""
    call_type: str = ""  # external_call, transfer, send, call, delegatecall, etc.
    target: str = ""  # 被调用的函数或地址
    value: Optional[str] = None  # msg.value或发送的金额
    gas: Optional[str] = None
    args: List[str] = field(default_factory=list)
    is_low_level: bool = False  # 是否是低级别调用


@dataclass
class StateChangeNode(ASTNode):
    """状态修改节点"""
    variable: str = ""  # 被修改的变量名
    operation: str = ""  # =, +=, -=, etc.


@dataclass
class AST:
    """完整的AST"""
    contracts: List[ContractNode] = field(default_factory=list)
    source_code: str = ""
    file_path: str = ""

