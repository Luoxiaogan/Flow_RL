
# InternBootcamp Problem Solving Workflow with Predefined Operators
import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from metagpt.workflow import Workflow
from metagpt.actions import ActionNode
from ScoreFlow.scripts.internbootcamp.operator import Custom, Review, Reflect, Programmer, ScEnsemble


class InternBootcampWorkflow(Workflow):
    """Workflow for adidyoumean using predefined operators"""
    
    def __init__(self, llm):
        super().__init__()
        self.llm = llm
        
    async def run(self, problem: Dict[str, Any]) -> str:
        # Initialize operators
        custom = Custom(self.llm, problem)
        review = Review(self.llm, problem)
        programmer = Programmer(self.llm, problem)
        ensemble = ScEnsemble(self.llm, problem)
        
        # Generate initial solution
        solution1 = await custom("Analyze the problem and provide a step-by-step solution.")
        
        # Review and improve
        solution2 = await review(solution1)
        
        # Generate code solution if applicable
        solution3 = await programmer("Write code to solve this problem")
        
        # Select best solution
        final_solution = await ensemble([solution1, solution2, solution3])
        
        return final_solution


# The workflow is ready to solve InternBootcamp problems
