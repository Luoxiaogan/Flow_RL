# Workflow ID: mbppplus_155_0
# Benchmark: mbppplus
# Data Indices: [336, 110]

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

        # PHASE 1: PROBLEM DISSECTION & SPECIFICATION
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into its core conceptual components. 
            Identify: 
            1. The exact input type(s) and format(s) expected
            2. The precise output type and format required
            3. Key operations or transformations needed
            4. Edge cases that must be handled (empty inputs, single elements, boundaries, etc.)
            5. Any ambiguities in the problem statement that need resolution
            6. Hidden constraints or assumptions
            Return structured subproblems focusing on specification, not implementation.""",
            context=""
        )
        
        specification = await self.generate(
            instruction=f"""Based on this problem decomposition:
            {decomposition}
            
            Generate a comprehensive, unambiguous specification document that:
            - Precisely defines input/output contracts including data types
            - Lists all edge cases that must be handled with examples
            - Resolves any ambiguities identified in decomposition
            - Specifies tie-breaking rules, ordering requirements, or special conditions
            - Defines what constitutes a correct solution
            Format as a structured markdown document with clear sections.""",
            context=str(decomposition)
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION
        strategy_instructions = [
            """Propose a solution strategy focusing on mathematical correctness and algorithmic efficiency. 
            Consider time/space complexity, optimal data structures, and mathematical properties. 
            Explicitly address how edge cases from the specification will be handled.""",
            
            """Propose a solution strategy focusing on robustness and defensive programming. 
            Prioritize handling all edge cases, input validation, and graceful failure. 
            Include fallback behaviors and error conditions even if not explicitly requested.""",
            
            """Propose a solution strategy focusing on code simplicity and readability. 
            Favor straightforward, maintainable implementations over clever optimizations. 
            Ensure the solution is easily verifiable against the specification."""
        ]

        strategies = await asyncio.gather(*[
            self.generate(
                instruction=f"""{instr}
                
                Base your strategy on this specification:
                {specification}
                
                Return a detailed step-by-step approach including:
                - Key algorithmic steps
                - Data structures to use
                - How edge cases are handled
                - Any trade-offs made""",
                context=specification
            ) for instr in strategy_instructions
        ])

        # Refine each strategy to ensure edge case coverage
        refined_strategies = await asyncio.gather(*[
            self.revise(
                instruction=f"""Enhance this strategy to ensure comprehensive edge case handling:
                - Verify all edge cases from specification are explicitly addressed
                - Add missing validation steps if necessary
                - Ensure type consistency throughout
                - Clarify any ambiguous steps
                - Maintain the original strategy's core approach while strengthening robustness""",
                context=strategy
            ) for strategy in strategies
        ])

        # PHASE 3: SYNTHESIS & EXECUTION
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the best elements from all strategies into a unified approach:
            - Combine mathematical efficiency with robustness and simplicity
            - Resolve any conflicts between strategies by prioritizing correctness and specification compliance
            - Ensure all edge cases are covered by at least one strategy's approach
            - Create a step-by-step implementation plan that is both optimal and maintainable
            - The final strategy should be ready for direct code implementation""",
            contexts_list=refined_strategies
        )

        # Generate code based on synthesized strategy
        code_result = await self.programmer(
            instruction=f"""Implement the solution according to this synthesized strategy:
            {synthesized_strategy}
            
            Requirements:
            - Use the exact function signature specified in the problem
            - Include all necessary imports
            - Handle all edge cases identified in the specification
            - Return the correct data type as specified
            - Code must be production-ready and pass all test cases
            - Include minimal but sufficient comments for clarity""",
            context=synthesized_strategy,
            max_retries=3
        )

        # Validation and refinement loop
        validation = await self.generate(
            instruction=f"""Critically validate this code against the original problem specification:
            {specification}
            
            Check:
            - Does it handle all specified edge cases?
            - Are input/output types correct?
            - Is the logic sound for all test scenarios?
            - Are there any potential bugs or oversights?
            - Does it match the expected behavior in sample test cases?
            
            If issues are found, provide specific revision instructions.
            If no issues, return 'VALIDATED'.""",
            context=code_result
        )

        final_code = code_result
        if "VALIDATED" not in validation.upper():
            # Revise code based on validation feedback
            final_code = await self.revise(
                instruction=f"""Revise the code to address these validation issues:
                {validation}
                
                Maintain the original function signature and core logic while fixing identified problems.
                Ensure all edge cases are properly handled.""",
                context=code_result
            )

        # Extract just the code portion from the final result
        code_lines = []
        in_code_block = False
        for line in final_code.split('\n'):
            if line.strip().startswith('