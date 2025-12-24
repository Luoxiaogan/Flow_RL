"""
Generate Tool for New_Flow_RL

根据指令生成文本内容，是最基础的工具之一。
"""

from typing import Any, Dict, Optional

from src.tools.base import PydanticTool, ToolResult
from src.tools.models import GenerateInput, GenerateOutput
from src.core.llm_call import LLMClient, LLMResponse
from src.core.logger import get_logger

logger = get_logger(__name__)


class GenerateTool(PydanticTool):
    """
    生成工具。

    根据指令和上下文生成文本内容。

    Usage:
        tool = GenerateTool(llm_client=client)
        result = tool(instruction="写一首关于春天的诗")
    """

    name = "generate"
    description = "根据指令和上下文生成文本内容。用于一般性的文本生成任务。"

    input_model = GenerateInput
    output_model = GenerateOutput

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化生成工具。

        Args:
            llm_client: LLM客户端（如不提供则从环境变量创建）
            config: 工具配置
        """
        super().__init__(config)
        self._llm_client = llm_client

    @property
    def llm_client(self) -> LLMClient:
        """懒加载 LLM 客户端"""
        if self._llm_client is None:
            self._llm_client = LLMClient.from_env()
        return self._llm_client

    def _execute(self, input_data: GenerateInput) -> GenerateOutput:
        """
        执行生成逻辑。

        Args:
            input_data: 验证后的输入

        Returns:
            GenerateOutput: 生成结果
        """
        # 构建消息
        messages = []

        # 如果有上下文，添加系统消息
        if input_data.context:
            messages.append({
                "role": "system",
                "content": f"Context:\n{input_data.context}"
            })

        # 添加用户指令
        messages.append({
            "role": "user",
            "content": input_data.instruction
        })

        # 调用 LLM
        response: LLMResponse = self.llm_client.call(
            messages=messages,
            model=input_data.model,
            temperature=input_data.temperature,
            max_tokens=input_data.max_tokens
        )

        return GenerateOutput(
            response=response.content,
            model=response.model,
            usage=response.usage
        )

    def get_parameters_schema(self) -> Dict[str, Any]:
        """获取参数 Schema"""
        return {
            "type": "object",
            "properties": {
                "instruction": {
                    "type": "string",
                    "description": "生成任务的指令"
                },
                "context": {
                    "type": "string",
                    "description": "可选的上下文信息"
                },
                "model": {
                    "type": "string",
                    "description": "使用的模型名称",
                    "default": "qwen-turbo"
                },
                "temperature": {
                    "type": "number",
                    "description": "采样温度",
                    "default": 0.7
                }
            },
            "required": ["instruction"]
        }


class AnswerTool(PydanticTool):
    """
    答案生成工具。

    综合上下文信息生成最终答案。

    Usage:
        tool = AnswerTool(llm_client=client)
        result = tool(
            question="法国的首都是哪里？",
            context="法国是欧洲国家，首都位于塞纳河畔。"
        )
    """

    name = "answer"
    description = "综合问题和上下文信息，生成结构化的最终答案。"

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(config)
        self._llm_client = llm_client

    @property
    def llm_client(self) -> LLMClient:
        if self._llm_client is None:
            self._llm_client = LLMClient.from_env()
        return self._llm_client

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行答案生成"""
        question = input_data.get("question", "")
        context = input_data.get("context", "")
        reasoning = input_data.get("reasoning", "")
        answer_format = input_data.get("format", "text")

        # 构建提示
        prompt = f"""Based on the following information, provide a clear and accurate answer.

Question: {question}

Context:
{context}
"""
        if reasoning:
            prompt += f"\nReasoning process:\n{reasoning}\n"

        prompt += f"""
Please provide:
1. A direct answer to the question
2. Your confidence level (0-1)
3. A brief explanation if needed

Format your response as:
Answer: [your answer]
Confidence: [0.0-1.0]
Explanation: [optional explanation]
"""

        response = self.llm_client.call(
            messages=prompt,
            temperature=0.3,  # 低温度以获得更确定的答案
            max_tokens=1024
        )

        # 解析响应
        content = response.content
        answer = content
        confidence = 0.5
        explanation = None

        # 简单解析（可以增强）
        lines = content.strip().split('\n')
        for line in lines:
            if line.startswith('Answer:'):
                answer = line[7:].strip()
            elif line.startswith('Confidence:'):
                try:
                    confidence = float(line[11:].strip())
                except ValueError:
                    pass
            elif line.startswith('Explanation:'):
                explanation = line[12:].strip()

        return {
            "answer": answer,
            "confidence": confidence,
            "explanation": explanation
        }

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "原始问题"
                },
                "context": {
                    "type": "string",
                    "description": "相关上下文信息"
                },
                "reasoning": {
                    "type": "string",
                    "description": "推理过程（可选）"
                },
                "format": {
                    "type": "string",
                    "description": "答案格式",
                    "enum": ["text", "number", "json", "code"],
                    "default": "text"
                }
            },
            "required": ["question", "context"]
        }


def create_generate_tool(
    llm_client: Optional[LLMClient] = None,
    config: Optional[Dict[str, Any]] = None
) -> GenerateTool:
    """
    工厂函数：创建生成工具。

    Args:
        llm_client: LLM客户端
        config: 工具配置

    Returns:
        GenerateTool 实例
    """
    return GenerateTool(llm_client=llm_client, config=config)


def create_answer_tool(
    llm_client: Optional[LLMClient] = None,
    config: Optional[Dict[str, Any]] = None
) -> AnswerTool:
    """
    工厂函数：创建答案工具。

    Args:
        llm_client: LLM客户端
        config: 工具配置

    Returns:
        AnswerTool 实例
    """
    return AnswerTool(llm_client=llm_client, config=config)
