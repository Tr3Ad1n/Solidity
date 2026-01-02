"""控制流分析"""

from typing import Dict, List, Set, Tuple
from ..parser.ast_builder import AST, FunctionNode, ContractNode


class ControlFlowGraph:
    """控制流图"""
    def __init__(self):
        self.nodes: List[str] = []  # 节点ID列表
        self.edges: List[Tuple[str, str]] = []  # 边列表 (from, to)
        self.node_labels: Dict[str, str] = {}  # 节点标签


class ControlFlowAnalyzer:
    """控制流分析器"""
    
    def analyze(self, ast: AST) -> Dict[str, ControlFlowGraph]:
        """
        分析控制流
        
        Args:
            ast: AST对象
            
        Returns:
            每个函数的控制流图
        """
        cfgs = {}
        
        for contract in ast.contracts:
            for func in contract.functions:
                cfg = self._build_cfg(func)
                key = f"{contract.name}.{func.name}"
                cfgs[key] = cfg
        
        return cfgs
    
    def _build_cfg(self, func: FunctionNode) -> ControlFlowGraph:
        """构建函数的控制流图"""
        cfg = ControlFlowGraph()
        
        # 简化版：基于函数体构建基本CFG
        body = func.body
        
        # 提取基本块（简化：基于控制结构）
        blocks = self._extract_blocks(body)
        
        # 添加节点
        for i, block in enumerate(blocks):
            node_id = f"block_{i}"
            cfg.nodes.append(node_id)
            cfg.node_labels[node_id] = block[:50] + "..." if len(block) > 50 else block
        
        # 添加边（顺序执行）
        for i in range(len(blocks) - 1):
            cfg.edges.append((f"block_{i}", f"block_{i+1}"))
        
        # 处理控制结构（if, while, for）
        self._process_control_structures(cfg, body, blocks)
        
        return cfg
    
    def _extract_blocks(self, body: str) -> List[str]:
        """提取基本块"""
        # 简化：按语句分割
        import re
        
        # 移除大括号
        body = body.strip('{}')
        
        # 按分号分割语句
        statements = re.split(r';(?![^{]*})', body)
        
        blocks = []
        current_block = []
        
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt:
                continue
            
            current_block.append(stmt)
            
            # 如果是控制结构，开始新块
            if any(keyword in stmt for keyword in ['if', 'while', 'for', 'return']):
                if current_block:
                    blocks.append('; '.join(current_block))
                    current_block = []
        
        if current_block:
            blocks.append('; '.join(current_block))
        
        return blocks if blocks else [body]
    
    def _process_control_structures(self, cfg: ControlFlowGraph, body: str, blocks: List[str]):
        """处理控制结构，添加条件边"""
        import re
        
        # 查找if语句
        if_pattern = re.compile(r'if\s*\([^)]+\)\s*\{', re.MULTILINE)
        for match in if_pattern.finditer(body):
            # 简化：添加条件分支边
            # 实际应该更精确地分析
            pass

