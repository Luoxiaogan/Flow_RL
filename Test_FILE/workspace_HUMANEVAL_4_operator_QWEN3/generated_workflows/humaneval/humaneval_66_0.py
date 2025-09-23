# Workflow ID: humaneval_66_0
# Benchmark: humaneval
# Data Indices: [158, 73]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio

        # Step 1: Parallel multi-perspective analysis
        analysis_tasks = [
            self.generate(
                instruction="""Analyze this problem from a MATHEMATICAL/LOGICAL perspective:
                - Identify numerical patterns, formulas, or invariants
                - Determine if solution requires counting, comparison, or transformation
                - Note any arithmetic or algorithmic relationships in examples
                - Suggest mathematical operators or functions that might be relevant
                Output as structured bullet points.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from a STRUCTURAL/DATA perspective:
                - Identify input and output data types and structures
                - Note how examples transform inputs to outputs
                - Determine if solution requires iteration, recursion, or aggregation
                - Suggest Python constructs (loops, comprehensions, built-ins) that fit
                Output as structured bullet points.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from an EDGE CASE/ROBUSTNESS perspective:
                - Identify boundary conditions from examples (empty, single, extreme values)
                - Note any tie-breaking or ordering rules
                - List potential failure modes or ambiguities
                - Suggest defensive checks or fallbacks needed
                Output as structured bullet points.""",
                context=""
            )
        ]
        
        analyses = await asyncio.gather(*analysis_tasks)
        
        # Step 2: Synthesize analyses into unified strategy
        strategy = await self.ensemble(
            instruction="""Synthesize the three analyses into a single, coherent solution strategy:
            - Combine mathematical insights with structural approaches
            - Integrate edge case handling into the core logic
            - Prioritize simplicity and directness (no over-engineering)
            - Specify exact function signature and return type
            - Outline step-by-step implementation plan
            Output as a clear, numbered plan.""",
            contexts_list=analyses
        )

        # Step 3: Generate initial solution
        initial_solution = await self.generate(
            instruction=f"""Implement the function EXACTLY as specified:
            - Use the ENTRY POINT function name precisely
            - Follow the strategy: {strategy}
            - Return type must match examples (int, float, str, etc.)
            - Handle all edge cases identified in analysis
            - Code must be minimal and direct—no extra features
            - Output ONLY the function code, no explanations or imports
            Example output format:
            def function_name(...):
                ...""",
            context=strategy
        )

        # Step 4: Critique and iterative refinement
        current_solution = initial_solution
        for iteration in range(3):  # Max 3 refinement rounds
            critique = await self.revise(
                instruction="""Critically audit this code:
                - Does it match the function name in ENTRY POINT?
                - Does it handle ALL examples in the docstring?
                - Are edge cases from analysis properly handled?
                - Is return type consistent with examples?
                - Is logic minimal and direct (no over-engineering)?
                - Are there any potential bugs or oversights?
                If perfect, respond 'VALID'. Otherwise, list specific issues and fixes needed.""",
                context=current_solution
            )
            
            if "VALID" in critique.upper() and len(critique) < 50:  # Confidence check
                break
                
            # Revise based on critique
            current_solution = await self.revise(
                instruction=f"""Revise the code to fix these issues:
                {critique}
                - Maintain exact function signature
                - Preserve correct return type
                - Keep code minimal and focused
                - Output ONLY the revised function code""",
                context=current_solution
            )

        # Step 5: Fallback generation if critique remains uncertain
        final_critique = await self.revise(
            instruction="Final validation: Is this solution robust and correct? Respond VALID or NOT VALID.",
            context=current_solution
        )
        
        if "NOT VALID" in final_critique.upper():
            # Generate alternative solution
            alt_solution = await self.generate(
                instruction=f"""Generate an ALTERNATIVE implementation:
                - Use a different approach than previous solution
                - Focus on simplicity and correctness
                - Handle all edge cases
                - Output ONLY the function code""",
                context=strategy
            )
            
            # Ensemble to pick best
            current_solution = await self.ensemble(
                instruction="""Select the better solution:
                - Prefer simpler, more direct implementations
                - Must handle all examples and edge cases
                - Must have correct function name and return type
                - Output ONLY the selected function code""",
                contexts_list=[current_solution, alt_solution]
            )

        return current_solution