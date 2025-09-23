# Workflow ID: mbppplus_52_0
# Benchmark: mbppplus
# Data Indices: [303, 63]

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

        # PHASE 1: Deep Problem Analysis & Specification Extraction
        problem_analysis = await self.generate(
            instruction="""Conduct a forensic analysis of this programming problem. Extract:
            1. Core task: What must the function compute or return?
            2. Input specifications: Data types, constraints, valid ranges
            3. Output specifications: Exact return type, format, edge behavior
            4. Hidden constraints: Implicit rules not stated but logically required
            5. Ambiguities: Any unclear requirements needing resolution
            6. Edge cases: Minimum/maximum values, empty inputs, type boundaries
            7. Problem category: Classify as MATHEMATICAL, STRUCTURAL, LOGICAL, or HYBRID
            Present as a structured markdown report with clear section headers.""",
            context=""
        )

        # PHASE 2: Parallel Solution Strategy Generation
        strategy_math, strategy_algo, strategy_defensive = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution strategy from a PURELY MATHEMATICAL perspective:
                - Focus on formulas, algebraic transformations, numerical properties
                - Ignore implementation details; think in terms of equations and invariants
                - Leverage mathematical theorems or identities if applicable
                - Base reasoning on this analysis: {problem_analysis}""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution strategy from an ALGORITHMIC perspective:
                - Focus on step-by-step procedures, loops, conditionals, data structures
                - Consider time/space complexity trade-offs
                - Identify iterative vs recursive approaches
                - Base reasoning on this analysis: {problem_analysis}""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution strategy from a DEFENSIVE PROGRAMMING perspective:
                - Focus exclusively on edge cases, input validation, error handling
                - List all possible failure modes and how to handle them
                - Ensure type safety and boundary condition robustness
                - Base reasoning on this analysis: {problem_analysis}""",
                context=problem_analysis
            )
        )

        # PHASE 3: Strategy Synthesis & Refinement
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the three strategies into one unified solution plan:
            - Prioritize correctness and robustness over elegance
            - Resolve conflicts by favoring defensive programming for edge cases
            - Incorporate mathematical optimizations where safe
            - Preserve algorithmic clarity for maintainability
            - Output must include explicit handling instructions for all edge cases identified""",
            contexts_list=[strategy_math, strategy_algo, strategy_defensive]
        )

        refined_strategy = await self.revise(
            instruction="""Refine this strategy into an executable specification:
            - Convert abstract ideas into concrete implementation steps
            - Specify exact variable names, loop conditions, return statements
            - Add type annotations and input validation checks
            - Format as a numbered checklist for code generation""",
            context=synthesized_strategy
        )

        # PHASE 4: Adaptive Code Generation with Validation Loop
        final_code = None
        error_log = ""
        
        for attempt in range(3):
            try:
                code_attempt = await self.programmer(
                    instruction=f"""Generate Python code that implements this exact specification:
                    {refined_strategy}
                    
                    Requirements:
                    - Use EXACT function name and signature from original problem
                    - Include all necessary imports inside the function if needed
                    - Handle ALL edge cases specified in the strategy
                    - Return correct data types (list vs tuple vs set matters)
                    - No wrapper functions or classes - only the requested function
                    - Code must be production-ready with no placeholders""",
                    context=refined_strategy,
                    max_retries=1
                )
                
                # Extract code block using regex to handle markdown formatting
                code_match = re.search(r'