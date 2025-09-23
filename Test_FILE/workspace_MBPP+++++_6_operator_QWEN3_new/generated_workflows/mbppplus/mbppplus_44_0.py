# Workflow ID: mbppplus_44_0
# Benchmark: mbppplus
# Data Indices: [244, 82]

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
        import math
        import re

        # Phase 1: Meta-Analysis & Problem Classification
        classification = await self.generate(
            instruction="""Perform deep problem classification. Analyze:
            1. Problem type: Mathematical formula, combinatorial search, string manipulation, data structure operation, or logic puzzle?
            2. Solution archetype: Closed-form equation, iterative algorithm, recursive approach, or heuristic?
            3. Edge case profile: What boundary conditions must be handled? (e.g., zero, negative, empty, single element)
            4. Computational constraints: Time/space complexity concerns? Large input handling?
            5. Output format: Exact type and structure required (int, bool, list, tuple, etc.)
            6. Known mathematical identities or theorems applicable?
            Provide structured classification with confidence scores for each dimension.""",
            context=""
        )

        # Phase 2: Strategy Generation (Parallel Multiple Approaches)
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate Strategy A: Mathematical/Analytical Approach
                Based on classification: {classification}
                - Derive closed-form solution if possible
                - Use mathematical identities, approximations, or transformations
                - Specify exact formulas and variable substitutions
                - Handle edge cases mathematically
                Output detailed step-by-step mathematical reasoning.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Strategy B: Algorithmic/Iterative Approach
                Based on classification: {classification}
                - Design brute-force or optimized search algorithm
                - Specify loop structures, termination conditions, and invariants
                - Include complexity analysis (time/space)
                - Handle edge cases programmatically
                Output pseudocode with detailed comments.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Strategy C: Hybrid Approach
                Based on classification: {classification}
                - Combine mathematical insights with algorithmic execution
                - Use formulas to bound search space or validate results
                - Specify where math ends and code begins
                - Include fallback mechanisms for edge cases
                Output integrated reasoning with clear phase transitions.""",
                context=""
            )
        ]
        strategy_candidates = await asyncio.gather(*strategy_tasks)

        # Phase 3: Strategy Selection via Ensemble
        selected_strategy = await self.ensemble(
            instruction="""Select optimal strategy based on:
            1. Correctness: Which approach handles all edge cases and constraints?
            2. Efficiency: Which has best time/space complexity for expected inputs?
            3. Robustness: Which is least prone to floating-point errors or overflow?
            4. Readability: Which is most maintainable and explainable?
            5. Generality: Which works for widest range of inputs in this domain?
            Justify selection with specific references to problem requirements.
            Output selected strategy with enhancement recommendations.""",
            contexts_list=strategy_candidates
        )

        # Phase 4: Hierarchical Decomposition
        decomposition = await self.decompose(
            instruction=f"""Decompose selected strategy into executable subproblems:
            Strategy: {selected_strategy}
            
            For each subproblem:
            - Specify exact mathematical or computational operation
            - Define input/output types and constraints
            - Identify dependencies on other subproblems
            - Include validation criteria for each step
            - Flag any steps requiring numerical precision handling
            Output as structured list with IDs and dependencies.""",
            context=selected_strategy
        )

        # Phase 5: Parallel Subproblem Solving
        subproblem_solutions = {}
        for subproblem in decomposition:
            sub_id = subproblem['id']
            deps = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
            
            # Wait for dependencies
            if deps and deps != ['']:
                await asyncio.gather(*[asyncio.sleep(0) for dep in deps if dep in subproblem_solutions])
            
            # Solve subproblem
            solution = await self.programmer(
                instruction=f"""Implement subproblem: {subproblem['description']}
                Context: {selected_strategy}
                Dependencies: {deps}
                Requirements:
                - Handle specified edge cases
                - Maintain numerical precision if needed
                - Return exact required data type
                - Include input validation
                - Optimize for performance within constraints
                Generate pure Python function with comprehensive error handling.""",
                context=subproblem['description']
            )
            subproblem_solutions[sub_id] = solution

        # Phase 6: Adversarial Validation & Revision Loop
        final_code = "\n\n".join(subproblem_solutions.values())
        for iteration in range(3):  # Max 3 revision cycles
            validator = await self.generate(
                instruction=f"""Critique this code rigorously:
                Code: {final_code}
                Original Problem: {self.problem_text}
                Classification: {classification}
                
                Check for:
                1. Edge case handling (zero, negative, empty, boundary values)
                2. Numerical precision issues (floating point, overflow)
                3. Algorithmic correctness (loop invariants, termination)
                4. Type consistency (input/output types match requirements)
                5. Performance bottlenecks
                6. Readability and maintainability
                Output detailed critique with specific line numbers and fixes.""",
                context=final_code
            )
            
            if "no issues found" in validator.lower() or "correct" in validator.lower():
                break
                
            final_code = await self.revise(
                instruction=f"""Revise code based on critique:
                Critique: {validator}
                Requirements:
                - Fix all identified issues
                - Maintain original functionality
                - Improve robustness without sacrificing performance
                - Add comments for complex sections
                Output complete revised code with changelog.""",
                context=final_code
            )

        # Phase 7: Final Synthesis & Output Extraction
        final_output = await self.generate(
            instruction=f"""Extract final function implementation from this code:
            {final_code}
            
            Requirements:
            - Must match exact function signature from problem
            - Include all necessary imports at top
            - Preserve all edge case handling
            - Return correct data type as specified
            - Remove any test code or print statements
            - Format as single code block with no additional text
            Output ONLY the function implementation in required format.""",
            context=final_code
        )

        # Phase 8: Summarize Reasoning (for traceability)
        await self.summarize(
            instruction=f"""Create executive summary of solution journey:
            - Problem classification
            - Strategy selection rationale
            - Key decomposition insights
            - Validation challenges overcome
            - Final implementation highlights
            Format as concise bullet points for future reference.""",
            context=final_output
        )

        return final_output