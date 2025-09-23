# Workflow ID: mbppplus_185_0
# Benchmark: mbppplus
# Data Indices: [242, 206]

import asyncio

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # Step 1: Semantic analysis of the problem
        problem_analysis = await self.generate(
            instruction="""Perform deep semantic analysis of this programming problem. Extract:
            1. Problem type (sequence generation, search/filter, transformation, validation, etc.)
            2. Key constraints (order preservation, uniqueness, termination conditions)
            3. Edge cases (empty inputs, single elements, boundary values, type edge cases)
            4. Implied algorithms (heap, DP, two-pointer, etc.)
            5. Expected return type and structure
            6. Any hints from function name or parameters
            Format as structured markdown with clear sections.""",
            context=""
        )

        # Step 2: Summarize into actionable spec
        problem_spec = await self.summarize(
            instruction="""Convert the analysis into a concise, structured specification for code generation:
            - Problem Type: [classification]
            - Strategy: [recommended approach]
            - Must Handle: [critical edge cases]
            - Return Type: [exact expected type]
            - Key Constraints: [bulleted list]
            Keep it under 200 words but preserve all critical details.""",
            context=problem_analysis
        )

        # Step 3: Generate edge case inventory in parallel with solution attempts
        edge_case_task = self.generate(
            instruction="""Generate comprehensive list of edge cases for this problem. Include:
            - Empty inputs
            - Single element inputs
            - Boundary values (0, 1, -1, max/min)
            - Duplicate handling
            - Type edge cases
            - Performance stress cases
            Format as Python list of test cases with expected outputs where possible.""",
            context=problem_spec
        )

        # Step 4: Parallel solution generation - multiple strategies
        solution_strategies = [
            """Implement using most straightforward approach. Prioritize readability and correctness. 
            Handle all edge cases mentioned in spec. Include type hints and comments for clarity.""",
            
            """Implement using most efficient algorithm possible. Optimize for time/space complexity. 
            Use advanced data structures if beneficial. Still handle all edge cases.""",
            
            """Implement mimicking reference solution style if detectable. Focus on elegance and minimalism. 
            Ensure robustness despite brevity."""
        ]

        solution_attempts = await asyncio.gather(
            *[self.programmer(
                instruction=f"{strategy} Problem spec: {problem_spec}",
                context=problem_spec
            ) for strategy in solution_strategies]
        )

        # Step 5: Validate solutions against edge cases
        async def validate_solution(solution, edge_cases):
            try:
                # Extract just the function code from solution
                code_match = re.search(r'