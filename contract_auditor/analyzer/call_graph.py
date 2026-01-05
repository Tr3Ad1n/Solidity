"""调用图分析"""

from typing import Dict, List, Set, Tuple
import networkx as nx
from ..parser.ast_builder import AST, FunctionNode, ContractNode, CallNode


class CallGraphAnalyzer:
    """调用图分析器"""
    
    def __init__(self):
        self.graph = nx.DiGraph()  # 有向图
    
    def analyze(self, ast: AST, clear: bool = True) -> nx.DiGraph:
        """
        构建调用图
        
        Args:
            ast: AST对象
            clear: 是否清空之前的图（默认True，用于单文件；False用于合并多文件）
            
        Returns:
            调用图（NetworkX DiGraph）
        """
        if clear:
            self.graph.clear()
        
        for contract in ast.contracts:
            contract_name = contract.name
            
            # 添加合约节点
            self.graph.add_node(contract_name, type='contract')
            
            # 添加函数节点
            for func in contract.functions:
                func_id = f"{contract_name}.{func.name}"
                self.graph.add_node(func_id, type='function', contract=contract_name, 
                                  function=func.name, line=func.line)
            
            # 添加调用边
            for func in contract.functions:
                func_id = f"{contract_name}.{func.name}"
                
                # 分析函数调用
                called_functions = self._extract_function_calls(func, contract, ast)
                
                for called_func in called_functions:
                    self.graph.add_edge(func_id, called_func, call_type='internal')
                
                # 分析外部调用
                external_calls = [c for c in func.calls if self._is_external_call(c)]
                for ext_call in external_calls:
                    ext_node = f"external_{ext_call.call_type}_{func.line}"
                    self.graph.add_node(ext_node, type='external_call', 
                                      call_type=ext_call.call_type)
                    self.graph.add_edge(func_id, ext_node, call_type='external')
        
        return self.graph
    
    def _extract_function_calls(self, func: FunctionNode, contract: ContractNode, 
                                ast: AST) -> List[str]:
        """提取函数调用"""
        called_functions = []
        
        # 从函数体中提取函数调用
        import re
        
        # 查找函数调用模式
        call_pattern = re.compile(r'(\w+)\s*\(', re.MULTILINE)
        
        for match in call_pattern.finditer(func.body):
            called_name = match.group(1)
            
            # 排除关键字
            keywords = ['if', 'while', 'for', 'require', 'assert', 'revert', 
                       'return', 'emit', 'new', 'delete']
            if called_name in keywords:
                continue
            
            # 检查是否是合约内的函数
            for other_func in contract.functions:
                if other_func.name == called_name:
                    called_functions.append(f"{contract.name}.{called_name}")
                    break
            
            # 检查是否是其他合约的函数
            for other_contract in ast.contracts:
                if other_contract.name == called_name:
                    # 可能是合约实例调用
                    continue
                for other_func in other_contract.functions:
                    if other_func.name == called_name:
                        called_functions.append(f"{other_contract.name}.{called_name}")
        
        return list(set(called_functions))  # 去重
    
    def _is_external_call(self, call: CallNode) -> bool:
        """判断是否是外部调用"""
        external_types = ['call', 'send', 'transfer', 'delegatecall', 'staticcall']
        return call.call_type in external_types or call.is_low_level
    
    def get_call_paths(self, from_func: str, to_func: str) -> List[List[str]]:
        """获取调用路径"""
        try:
            paths = list(nx.all_simple_paths(self.graph, from_func, to_func))
            return paths
        except:
            return []
    
    def to_simple_text(self) -> str:
        """生成简单的文本格式调用图"""
        if not self.graph.nodes():
            return "调用图为空"
        
        lines = []
        
        # 按合约分组
        contracts = {}
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            node_type = node_data.get('type', 'unknown')
            
            if node_type == 'contract':
                contract_name = node
                if contract_name not in contracts:
                    contracts[contract_name] = {'functions': []}
            elif node_type == 'function':
                contract_name = node_data.get('contract', '')
                if contract_name not in contracts:
                    contracts[contract_name] = {'functions': []}
                func_name = node_data.get('function', node)
                contracts[contract_name]['functions'].append((node, func_name))
        
        # 为每个合约生成调用图
        for contract_name, data in contracts.items():
            lines.append(f"\n【{contract_name}】")
            
            # 只显示有调用关系的函数
            has_calls = False
            for func_id, func_name in data['functions']:
                # 查找这个函数调用的其他函数
                out_edges = list(self.graph.out_edges(func_id))
                if out_edges:
                    has_calls = True
                    for edge in out_edges:
                        target = edge[1]
                        target_data = self.graph.nodes[target]
                        edge_data = self.graph.edges[edge]
                        call_type = edge_data.get('call_type', 'internal')
                        
                        if target_data.get('type') == 'function':
                            target_func = target_data.get('function', target)
                            lines.append(f"  {func_name} → {target_func}")
                        elif target_data.get('type') == 'external_call':
                            ext_type = target_data.get('call_type', 'call')
                            lines.append(f"  {func_name} → [外部调用: {ext_type}]")
            
            if not has_calls:
                lines.append("  (无调用关系)")
        
        return "\n".join(lines) if lines else "无调用关系"
    
    def to_dict(self) -> Dict:
        """转换为字典格式（用于JSON报告）"""
        nodes = []
        edges = []
        
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            nodes.append({
                "id": node,
                "type": node_data.get('type', 'unknown'),
                "label": node_data.get('function', node_data.get('contract', node))
            })
        
        for edge in self.graph.edges():
            edge_data = self.graph.edges[edge]
            edges.append({
                "from": edge[0],
                "to": edge[1],
                "type": edge_data.get('call_type', 'unknown')
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "simple_text": self.to_simple_text()  # 添加简单文本图
        }

