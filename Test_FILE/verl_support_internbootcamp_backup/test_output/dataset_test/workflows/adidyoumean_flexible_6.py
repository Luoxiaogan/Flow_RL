
# InternBootcamp Problem Solving Workflow with FlexibleCustom Operator
import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from metagpt.workflow import Workflow
from metagpt.actions import ActionNode
from ScoreFlow.scripts.internbootcamp.operator import FlexibleCustom


class InternBootcampWorkflow(Workflow):
    """Workflow for adidyoumean using FlexibleCustom operator"""
    
    def __init__(self, llm):
        super().__init__()
        self.llm = llm
        
    async def run(self, problem: Dict[str, Any]) -> str:
        # Initialize FlexibleCustom operator
        flexible = FlexibleCustom(self.llm, problem)
        
        # Use iterative reasoning pattern
        result = await flexible(
            custom_instruction="Solve this adidyoumean problem using logical reasoning and systematic approach.",
            reasoning_pattern="iterative",
            steps=["understand", "analyze", "solve", "verify"],
            max_iterations=3,
            use_structured_output=True
        )
        
        return result


# The workflow is ready to solve InternBootcamp problems
