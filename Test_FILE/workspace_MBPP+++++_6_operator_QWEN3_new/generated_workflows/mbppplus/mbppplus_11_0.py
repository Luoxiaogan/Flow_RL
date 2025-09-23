# Workflow ID: mbppplus_11_0
# Benchmark: mbppplus
# Data Indices: [211, 360]

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

        # Phase 1: Decompose the problem to understand its structure
        decomposition = await self.decompose(
            instruction="""Thoroughly analyze this programming problem and break it down into its essential components. For each component, provide a detailed description. Specifically identify:
            1. Input type and structure (e.g., string, list of integers, etc.)
            2. Expected output type and structure
            3. Core transformation or operation required (e.g., substitution, parsing, calculation, filtering)
            4. Any explicit or implicit constraints or edge cases (e.g., empty inputs, case sensitivity, boundary values)
            5. At least two inferred or explicit example input-output pairs, even if not directly stated
            6. Category of problem (e.g., string manipulation, mathematical computation, data structure operation)
            Format each subproblem clearly with these labels.""",
            context=""
        )

        # Summarize decomposition for concise context
        decomposition_summary = await self.summarize(
            instruction="Extract and condense the most critical information from the problem decomposition: input/output types, transformation category, key constraints, and example cases. Format as a compact, structured summary.",
            context=str(decomposition)
        )

        # Phase 2: Parallel solution generation
        # Branch 1: Generate natural language algorithm description
        nl_algorithm = await self.generate(
            instruction=f"""Based on the problem decomposition:
            {decomposition_summary}
            
            Describe the exact algorithm or logic needed to solve this problem in clear, step-by-step natural language. Include how to handle edge cases and ensure type consistency. Be precise enough that a programmer could implement it without ambiguity.""",
            context=decomposition_summary
        )

        # Branch 2: Direct code generation from problem text
        direct_code = await self.programmer(
            instruction=f"""Implement a Python function that solves the problem exactly as specified. The solution must:
            - Match the expected function signature
            - Handle all edge cases mentioned or implied
            - Return the correct data type
            - Be efficient and readable
            - Include necessary imports within the function if needed
            Base your implementation on the original problem description and any inferred requirements.""",
            context="",
            max_retries=2
        )

        # Branch 3: Code generation guided by decomposition
        guided_code = await self.programmer(
            instruction=f"""Using this problem analysis:
            {decomposition_summary}
            
            And this algorithm description:
            {nl_algorithm}
            
            Write a precise Python implementation. Ensure:
            - Correct function signature
            - Proper handling of edge cases listed in the decomposition
            - Return type matches exactly what's expected
            - Include any necessary imports (e.g., 'import re' for regex)
            - Code is clean, efficient, and well-commented""",
            context=nl_algorithm,
            max_retries=2
        )

        # Phase 3: Ensemble and validation
        candidate_solutions = [direct_code, guided_code]
        
        final_solution = await self.ensemble(
            instruction=f"""You are given multiple candidate solutions for a programming problem. Your task is to select or synthesize the best solution based on:
            1. Correctness: Does it match the expected input-output behavior? Verify against these examples: {decomposition_summary}
            2. Robustness: Does it handle edge cases properly?
            3. Type consistency: Does it return exactly the expected type (list, tuple, int, etc.)?
            4. Code quality: Is it clean, efficient, and readable?
            If no solution is perfect, synthesize a new one by combining the best parts of each. Return ONLY the final Python function code, with necessary imports included inside the function if needed.""",
            contexts_list=candidate_solutions
        )

        # Optional refinement loop (up to 2 iterations)
        refined_solution = final_solution
        for _ in range(2):
            validation = await self.generate(
                instruction=f"""Critically review this solution:
                {refined_solution}
                
                Check for:
                - Type mismatches (e.g., returning list when tuple expected)
                - Missing edge case handling
                - Logical errors or inefficiencies
                - Deviations from problem requirements
                If any issues are found, describe them specifically. If perfect, say 'VALID'.""",
                context=refined_solution
            )
            
            if "VALID" in validation or "valid" in validation:
                break
            else:
                refined_solution = await self.revise(
                    instruction=f"""Fix the following issues in the code:
                    {validation}
                    
                    Preserve the function signature and ensure type consistency. Return the complete corrected function.""",
                    context=refined_solution
                )

        return refined_solution