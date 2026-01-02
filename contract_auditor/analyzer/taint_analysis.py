"""污点分析"""

from typing import Dict, List, Set, Tuple
from ..parser.ast_builder import AST, FunctionNode, ContractNode, CallNode, StateChangeNode


class TaintSource:
    """污点源"""
    def __init__(self, name: str, line: int, source_type: str):
        self.name = name
        self.line = line
        self.type = source_type  # 'parameter', 'msg.sender', 'msg.value', 'external_call'


class TaintSink:
    """污点汇（危险操作）"""
    def __init__(self, name: str, line: int, sink_type: str):
        self.name = name
        self.line = line
        self.type = sink_type  # 'external_call', 'state_change', 'delegatecall'


class TaintPath:
    """污点传播路径"""
    def __init__(self, source: TaintSource, sink: TaintSink, path: List[str]):
        self.source = source
        self.sink = sink
        self.path = path  # 变量传播路径


class TaintAnalyzer:
    """污点分析器"""
    
    def analyze(self, ast: AST) -> List[TaintPath]:
        """
        执行污点分析
        
        Args:
            ast: AST对象
            
        Returns:
            污点传播路径列表
        """
        taint_paths = []
        
        for contract in ast.contracts:
            for func in contract.functions:
                # 识别污点源
                sources = self._identify_taint_sources(func)
                
                # 识别污点汇
                sinks = self._identify_taint_sinks(func)
                
                # 追踪污点传播
                for source in sources:
                    for sink in sinks:
                        path = self._trace_taint(func, source, sink)
                        if path:
                            taint_paths.append(TaintPath(source, sink, path))
        
        return taint_paths
    
    def _identify_taint_sources(self, func: FunctionNode) -> List[TaintSource]:
        """识别污点源"""
        sources = []
        
        import re
        
        # 函数参数
        for param in func.parameters:
            if 'address' in param.lower() or 'uint' in param.lower():
                sources.append(TaintSource(param, func.line, 'parameter'))
        
        # msg.sender
        if re.search(r'\bmsg\.sender\b', func.body, re.IGNORECASE):
            sources.append(TaintSource('msg.sender', func.line, 'msg.sender'))
        
        # msg.value
        if re.search(r'\bmsg\.value\b', func.body, re.IGNORECASE):
            sources.append(TaintSource('msg.value', func.line, 'msg.value'))
        
        # 外部调用返回值
        for call in func.calls:
            if self._is_external_call(call):
                sources.append(TaintSource(f"external_call_{call.line}", call.line, 'external_call'))
        
        return sources
    
    def _identify_taint_sinks(self, func: FunctionNode) -> List[TaintSink]:
        """识别污点汇（危险操作）"""
        sinks = []
        
        # 外部调用
        for call in func.calls:
            if self._is_external_call(call):
                sinks.append(TaintSink(f"external_call_{call.line}", call.line, 'external_call'))
            
            if call.call_type == 'delegatecall':
                sinks.append(TaintSink(f"delegatecall_{call.line}", call.line, 'delegatecall'))
        
        # 状态修改（如果涉及用户输入）
        for change in func.state_changes:
            sinks.append(TaintSink(f"state_change_{change.variable}", change.line, 'state_change'))
        
        return sinks
    
    def _trace_taint(self, func: FunctionNode, source: TaintSource, sink: TaintSink) -> List[str]:
        """追踪污点传播路径"""
        # 简化版污点追踪
        # 实际应该进行更精确的数据流分析
        
        path = []
        
        # 检查source和sink是否在同一个函数中
        if source.line <= sink.line:
            # 简单检查：如果source在sink之前，可能存在传播
            import re
            
            # 查找source到sink之间的变量使用
            body_lines = func.body.split('\n')
            source_line_idx = source.line - 1 if source.line <= len(body_lines) else 0
            sink_line_idx = sink.line - 1 if sink.line <= len(body_lines) else len(body_lines) - 1
            
            if source_line_idx < sink_line_idx:
                # 检查中间是否有相关变量
                middle_code = '\n'.join(body_lines[source_line_idx:sink_line_idx+1])
                
                # 简化：如果source名称出现在中间代码中，认为有传播
                if re.search(rf'\b{source.name}\b', middle_code, re.IGNORECASE):
                    path = [source.name, sink.name]
        
        return path
    
    def _is_external_call(self, call: CallNode) -> bool:
        """判断是否是外部调用"""
        external_types = ['call', 'send', 'transfer', 'delegatecall', 'staticcall']
        return call.call_type in external_types or call.is_low_level
    
    def to_dict(self, taint_paths: List[TaintPath]) -> List[Dict]:
        """转换为字典格式"""
        result = []
        for path in taint_paths:
            result.append({
                "source": {
                    "name": path.source.name,
                    "line": path.source.line,
                    "type": path.source.type
                },
                "sink": {
                    "name": path.sink.name,
                    "line": path.sink.line,
                    "type": path.sink.type
                },
                "path": path.path
            })
        return result

