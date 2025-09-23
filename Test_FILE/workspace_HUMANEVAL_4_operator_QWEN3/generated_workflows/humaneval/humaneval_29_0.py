# Workflow ID: humaneval_29_0
# Benchmark: humaneval
# Data Indices: [54, 99]

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

    async def run_workflow(self):
        import asyncio
        import re

        # Stage 1: Deep Analysis - Extract key patterns, constraints, and edge cases
        analysis = await self.generate(
            instruction="""Perform deep structural analysis of the problem specification:
            1. Identify the core task: What transformation or decision must the function perform?
            2. Extract all examples from the docstring and list them explicitly
            3. Identify patterns or rules that govern the expected behavior
            4. Note any edge cases or special conditions revealed by examples
            5. Determine required return type (int, float, bool, etc.) from examples
            6. Identify any mathematical, logical, or string manipulation patterns
            7. Note any constraints on input format or range
            8. Summarize the behavioral contract the function must satisfy
            
            Format your response as a structured analysis with clear sections.""",
            context=""
        )

        # Stage 2: Parallel Solution Generation - Three distinct approaches
        literal_approach = self.generate(
            instruction=f"""Generate a solution based on LITERAL interpretation of examples:
            - Study each example in the specification: {analysis}
            - Implement the minimal code that reproduces exactly the behavior shown
            - Do not generalize beyond what examples demonstrate
            - Focus on direct pattern matching or exact condition handling
            - Return type must match examples precisely (int vs float matters)
            - Function name must match ENTRY POINT exactly
            
            Provide ONLY the Python function code, nothing else.""",
            context=analysis
        )

        pattern_approach = self.generate(
            instruction=f"""Generate a solution based on PATTERN GENERALIZATION:
            - Analyze the underlying mathematical, logical, or algorithmic pattern: {analysis}
            - Implement a generalized solution that captures the core rule
            - Use appropriate Python constructs (math operations, string methods, etc.)
            - Handle edge cases identified in analysis
            - Return type must match examples precisely
            - Function name must match ENTRY POINT exactly
            
            Provide ONLY the Python function code, nothing else.""",
            context=analysis
        )

        edgecase_approach = self.generate(
            instruction=f"""Generate a solution with FOCUS ON EDGE CASES:
            - Prioritize handling all edge cases and boundary conditions: {analysis}
            - Implement defensive code that explicitly checks for special cases
            - Ensure robustness against inputs not shown in examples
            - Return type must match examples precisely
            - Function name must match ENTRY POINT exactly
            - Include explicit condition handling for identified edge cases
            
            Provide ONLY the Python function code, nothing else.""",
            context=analysis
        )

        # Execute parallel generation
        literal_code, pattern_code, edgecase_code = await asyncio.gather(
            literal_approach, pattern_approach, edgecase_approach
        )

        # Stage 3: Parallel Validation - Generate validation report for each candidate
        validate_literal = self.generate(
            instruction=f"""Act as a strict code reviewer and tester:
            Given this candidate solution:
            {literal_code}
            
            And this problem analysis:
            {analysis}
            
            Validate against specification:
            1. Does it handle ALL examples correctly?
            2. Does it address identified edge cases?
            3. Is return type correct and precise?
            4. Is function name exactly as specified?
            5. Is the solution minimal (no over-engineering)?
            6. Are there any logical flaws or boundary condition failures?
            
            Rate 1-10 on correctness and provide detailed critique.
            Format: "SCORE: X/10 | [detailed validation report]" """,
            context=literal_code
        )

        validate_pattern = self.generate(
            instruction=f"""Act as a strict code reviewer and tester:
            Given this candidate solution:
            {pattern_code}
            
            And this problem analysis:
            {analysis}
            
            Validate against specification:
            1. Does it handle ALL examples correctly?
            2. Does it address identified edge cases?
            3. Is return type correct and precise?
            4. Is function name exactly as specified?
            5. Is the solution minimal (no over-engineering)?
            6. Are there any logical flaws or boundary condition failures?
            
            Rate 1-10 on correctness and provide detailed critique.
            Format: "SCORE: X/10 | [detailed validation report]" """,
            context=pattern_code
        )

        validate_edgecase = self.generate(
            instruction=f"""Act as a strict code reviewer and tester:
            Given this candidate solution:
            {edgecase_code}
            
            And this problem analysis:
            {analysis}
            
            Validate against specification:
            1. Does it handle ALL examples correctly?
            2. Does it address identified edge cases?
            3. Is return type correct and precise?
            4. Is function name exactly as specified?
            5. Is the solution minimal (no over-engineering)?
            6. Are there any logical flaws or boundary condition failures?
            
            Rate 1-10 on correctness and provide detailed critique.
            Format: "SCORE: X/10 | [detailed validation report]" """,
            context=edgecase_code
        )

        # Execute parallel validation
        val_literal, val_pattern, val_edgecase = await asyncio.gather(
            validate_literal, validate_pattern, validate_edgecase
        )

        # Stage 4: Ensemble Selection - Choose best candidate based on validation
        selected_code = await self.ensemble(
            instruction=f"""Select the best solution based on validation reports:
            Candidate 1 (Literal approach): {val_literal}
            Candidate 2 (Pattern approach): {val_pattern} 
            Candidate 3 (Edge case approach): {val_edgecase}
            
            Selection criteria:
            1. Highest validation score
            2. Most comprehensive edge case handling
            3. Cleanest, most minimal implementation
            4. Best match to specification examples
            
            If multiple candidates have similar scores, synthesize a hybrid solution.
            Return ONLY the final Python function code, nothing else.""",
            contexts_list=[literal_code, pattern_code, edgecase_code]
        )

        # Stage 5: Precision Refinement - Ensure exact conformance
        final_code = await self.revise(
            instruction=f"""Refine this code for exact specification conformance:
            {selected_code}
            
            Critical checks:
            1. Function name must match ENTRY POINT exactly (verify spelling and case)
            2. Return type must match examples precisely (int vs float - check examples in {analysis})
            3. Handle all edge cases identified in analysis
            4. No over-engineering - implement exactly what's specified
            5. Code must be minimal and clean
            6. Must pass all examples in specification
            
            Return ONLY the refined Python function code, nothing else.""",
            context=selected_code
        )

        return final_code