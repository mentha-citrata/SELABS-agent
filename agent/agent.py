"""Agent 核心逻辑模块 - 使用 LangGraph 构建 ReAct Agent"""

from typing import Callable, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import Tool

from config.llm_config import get_llm
from tools.tool_definitions import TOOLS
from agent.state import AgentState
from utils.error_handler import handle_api_error, handle_llm_error


class LabAgent:
    """实验室管理 Agent 类"""
    
    def __init__(self):
        """初始化 Agent"""
        self.llm = get_llm()
        self.tools = TOOLS
        
        # 将工具转换为可被 LLM 使用的格式
        self.tools_by_name = {tool.name: tool for tool in self.tools}
        
        # 构建 StateGraph
        self.graph = self._build_graph()
        self.runnable_graph = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """构建 Agent 的 StateGraph
        
        Returns:
            StateGraph: 编译前的状态图
        """
        graph = StateGraph(AgentState)
        
        # 添加节点
        graph.add_node("agent", self._agent_node)
        graph.add_node("tool_executor", self._tool_executor_node)
        graph.add_node("end", self._end_node)
        
        # 设置入口点
        graph.set_entry_point("agent")
        
        # 添加条件边：如果是工具调用，转到 tool_executor；否则直接结束
        graph.add_conditional_edges(
            "agent",
            self._should_use_tool,
            {
                "tool": "tool_executor",
                "end": "end"
            }
        )
        
        # 从 tool_executor 返回 agent 进行循环
        graph.add_edge("tool_executor", "agent")
        
        # 设置结束节点
        graph.add_edge("end", END)
        
        return graph
    
    def _agent_node(self, state: AgentState) -> AgentState:
        """Agent 思考节点 - 调用 LLM 处理消息
        
        Args:
            state: 当前状态
            
        Returns:
            AgentState: 更新后的状态
        """
        try:
            # 使用 bind_tools 让 LLM 能够调用工具
            llm_with_tools = self.llm.bind_tools(self.tools)
            
            # 调用 LLM
            response = llm_with_tools.invoke(state["messages"])
            
            # 将 LLM 响应添加到消息列表
            state["messages"].append(response)
            
            return state
            
        except Exception as e:
            # LLM 调用失败，返回错误消息
            error_msg = handle_llm_error(e)
            state["messages"].append(AIMessage(content=error_msg))
            return state
    
    def _tool_executor_node(self, state: AgentState) -> AgentState:
        """工具执行节点 - 执行 LLM 选择的工具
        
        Args:
            state: 当前状态
            
        Returns:
            AgentState: 更新后的状态
        """
        # 获取最后一条消息（应该是 LLM 的工具调用消息）
        last_message = state["messages"][-1]
        
        # 检查是否有工具调用
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return state
        
        # 执行所有工具调用
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_input = tool_call["args"]
            
            try:
                # 获取工具并调用
                if tool_name in self.tools_by_name:
                    tool = self.tools_by_name[tool_name]
                    result = tool.invoke(tool_input)
                else:
                    result = {"error": f"未知工具: {tool_name}"}
                    
            except Exception as e:
                # 工具调用失败
                result = {"error": handle_api_error(e)}
            
            # 将工具结果添加到消息列表
            state["messages"].append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                    name=tool_name
                )
            )
        
        return state
    
    def _should_use_tool(self, state: AgentState) -> str:
        """条件边函数 - 判断是否需要调用工具
        
        Args:
            state: 当前状态
            
        Returns:
            str: "tool" 或 "end"
        """
        last_message = state["messages"][-1]
        
        # 如果最后一条消息有工具调用，则使用工具
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tool"
        else:
            return "end"
    
    def _end_node(self, state: AgentState) -> AgentState:
        """结束节点 - 返回最终响应
        
        Args:
            state: 当前状态
            
        Returns:
            AgentState: 最终状态
        """
        return state
    
    def run(self, user_message: str) -> str:
        """运行 Agent - 处理用户输入并返回响应
        
        Args:
            user_message: 用户输入的消息
            
        Returns:
            str: Agent 的响应
        """
        # 创建初始状态
        initial_state = {
            "messages": [HumanMessage(content=user_message)]
        }
        
        # 运行 Agent
        final_state = self.runnable_graph.invoke(initial_state)
        
        # 提取最后一条消息作为响应
        last_message = final_state["messages"][-1]
        
        if isinstance(last_message, AIMessage):
            return last_message.content
        elif isinstance(last_message, ToolMessage):
            return last_message.content
        else:
            return str(last_message)
    
    def run_with_history(self, messages: list[str]) -> str:
        """运行 Agent - 处理多轮对话
        
        Args:
            messages: 消息列表，其中最后一条是新的用户消息
            
        Returns:
            str: Agent 的响应
        """
        # 构建消息历史
        message_objects = []
        for i, msg in enumerate(messages):
            if i % 2 == 0:  # 偶数索引为用户消息
                message_objects.append(HumanMessage(content=msg))
            else:  # 奇数索引为 Agent 响应
                message_objects.append(AIMessage(content=msg))
        
        # 创建状态
        state = {
            "messages": message_objects
        }
        
        # 运行 Agent
        final_state = self.runnable_graph.invoke(state)
        
        # 提取最后一条 AI 消息作为响应
        for msg in reversed(final_state["messages"]):
            if isinstance(msg, AIMessage):
                return msg.content
        
        return "无法获取响应"
