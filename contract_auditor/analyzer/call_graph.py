"""调用图分析"""

from typing import Dict, List, Set, Tuple
import networkx as nx
from ..parser.ast_builder import AST, FunctionNode, ContractNode, CallNode


class CallGraphAnalyzer:
    """调用图分析器"""
    
    def __init__(self):
        self.graph = nx.DiGraph()  # 有向图
    
    def analyze(self, ast: AST) -> nx.DiGraph:
        """
        构建调用图
        
        Args:
            ast: AST对象
            
        Returns:
            调用图（NetworkX DiGraph）
        """
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
            "edges": edges
        }

