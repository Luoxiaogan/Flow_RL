# Workflow ID: mbppplus_80_0
# Benchmark: mbppplus
# Data Indices: [112, 192]

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

        # Phase 1: Problem Decomposition
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into its fundamental subproblems. 
            For each subproblem, identify:
            - The input data types and structures
            - The expected output and its type
            - Key operations or algorithms needed
            - Edge cases to consider (empty inputs, single elements, boundaries, duplicates)
            - Any implicit constraints or assumptions
            Return a structured list of subproblems with clear descriptions and dependencies.""",
            context=""
        )

        # Phase 2: Parallel Analysis - Explore multiple solution perspectives
        mathematical_analysis, data_structure_analysis, edge_case_analysis = await asyncio.gather(
            self.generate(
                instruction="""Analyze this problem from a mathematical/logical perspective.
                - What formal logic, set theory, or algorithmic patterns apply?
                - Can the problem be reduced to a known computational pattern (e.g., search, sort, filter)?
                - What invariants or properties must be preserved?
                - How can correctness be formally verified?
                Provide a detailed, step-by-step logical analysis.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from a data structure and algorithm perspective.
                - What data structures are involved (lists, tuples, sets, etc.)?
                - What operations are most efficient for this data (iteration, recursion, hashing, etc.)?
                - Are there ordering or uniqueness constraints?
                - What is the optimal time/space complexity?
                Provide a detailed analysis with algorithmic recommendations.""",
                context=""
            ),
            self.generate(
                instruction="""Generate a comprehensive list of edge cases and boundary conditions.
                - Consider empty inputs, single-element inputs, extreme values, duplicates, and type variations.
                - For each edge case, specify the expected behavior and why.
                - Identify any silent failure modes or common pitfalls.
                - Suggest defensive programming techniques to handle these cases.
                Provide a detailed, categorized list of edge cases with handling strategies.""",
                context=""
            )
        )

        # Phase 3: Strategy Synthesis
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the mathematical, data structure, and edge case analyses into a unified solution strategy.
            - Resolve any contradictions between analyses.
            - Prioritize robustness and correctness over performance (unless performance is explicitly required).
            - Select the most appropriate algorithmic approach based on the analyses.
            - Incorporate edge case handling as first-class requirements.
            - Output a step-by-step implementation plan that a programmer can follow.
            The strategy should be detailed enough to guide code generation without ambiguity.""",
            contexts_list=[mathematical_analysis, data_structure_analysis, edge_case_analysis]
        )

        # Phase 4: Iterative Code Generation and Refinement
        code_attempt = await self.programmer(
            instruction=f"""Implement the solution according to this strategy:
            {synthesized_strategy}
            
            Requirements:
            - Match the exact function signature from the problem.
            - Handle all edge cases identified in the edge case analysis.
            - Include comments explaining key steps and decisions.
            - Return the correct data type (list, tuple, set, etc.) as specified.
            - Do not include any test cases or print statements.
            Generate clean, production-ready code.""",
            context=synthesized_strategy
        )

        # Refine the code up to 2 times
        for iteration in range(2):
            refined_code = await self.revise(
                instruction=f"""Critique this code for:
                - Correctness: Does it solve the problem as specified?
                - Edge case handling: Does it handle all identified edge cases?
                - Efficiency: Is the algorithm appropriate for the problem size?
                - Code quality: Is it readable, well-commented, and follows best practices?
                - Type safety: Does it return the correct data type?
                Suggest specific, actionable improvements. If no improvements are needed, return the original code unchanged.""",
                context=code_attempt
            )
            if refined_code.strip() == code_attempt.strip():
                break  # No changes needed
            code_attempt = refined_code

        # Phase 5: Validation and Final Output
        validation = await self.generate(
            instruction=f"""Generate a comprehensive set of test cases for this solution, including:
            - Basic functionality tests
            - Edge cases (empty inputs, single elements, boundaries, duplicates)
            - Type variation tests (if applicable)
            - Performance boundary tests (if applicable)
            For each test case, explain why it is important and what it verifies.
            Then, verify that the code handles all cases correctly. If any failures are found, suggest fixes.""",
            context=code_attempt
        )

        # Final revision based on validation (optional, for robustness)
        final_code = await self.revise(
            instruction=f"""Incorporate any fixes suggested by the validation phase.
            If no fixes are needed, return the code unchanged.
            Ensure the code is production-ready and handles all edge cases robustly.""",
            context=code_attempt + "\n\nVALIDATION FEEDBACK:\n" + validation
        )

        return final_code