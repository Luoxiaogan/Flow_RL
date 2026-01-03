# Workflow ID: limr_39_0
# Benchmark: limr
# Data Indices: [137, 248]

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

        # PHASE 1: PROBLEM TRIAGE & STRATEGY CLASSIFICATION
        classification = await self.generate(
            instruction="""Perform deep problem classification for LIMR domain. Analyze along these dimensions:
            1. Primary mathematical domain (number theory, algebra, combinatorics, geometry, probability, etc.)
            2. Required techniques (modular arithmetic, induction, coordinate geometry, generating functions, etc.)
            3. Computational complexity (symbolic manipulation, heavy computation, combinatorial search, etc.)
            4. Answer constraints (must be integer 000-999, specific range like 0-55, etc.)
            5. Potential solution approaches (direct computation, proof by contradiction, case analysis, etc.)
            6. Known pitfalls or common errors for this problem type
            7. Recommended verification strategies
            Format as structured JSON with keys: domain, techniques, complexity, constraints, approaches, pitfalls, verification""",
            context=""
        )

        # PHASE 2: PARALLEL SOLUTION STRATEGY GENERATION
        # Three complementary approaches run in parallel
        symbolic_approach = self.generate(
            instruction=f"""Develop a complete symbolic/mathematical solution approach based on classification:
            Classification: {classification}
            
            Requirements:
            - Use pure mathematical reasoning without code
            - Show all algebraic/trigonometric/combinatorial steps
            - Maintain exact precision (no approximations)
            - Verify intermediate results where possible
            - Ensure final answer meets constraints: {classification}
            - Format final answer as integer 000-999 with leading zeros if needed""",
            context=""
        )

        code_approach = self.generate(
            instruction=f"""Design a computational solution approach based on classification:
            Classification: {classification}
            
            Requirements:
            - Focus on algorithmic implementation
            - Specify exact functions/algorithms needed (e.g., extended Euclidean for modular inverse)
            - Handle edge cases and boundary conditions
            - Ensure output format: integer 000-999
            - Include verification steps in code design
            - Optimize for correctness over performance""",
            context=""
        )

        decomposed_approach = self.decompose(
            instruction=f"""Break problem into minimal necessary subproblems based on classification:
            Classification: {classification}
            
            Requirements:
            - Identify atomic computational or logical steps
            - Specify dependencies between subproblems
            - Include verification subproblems for critical steps
            - Ensure final subproblem produces answer in 000-999 format
            - Maximum 7 subproblems for efficiency""",
            context=""
        )

        # Execute parallel generation
        symbolic_result, code_design, decomposition = await asyncio.gather(
            symbolic_approach,
            code_approach,
            decomposed_approach
        )

        # Summarize decomposition for easier processing
        decomposition_summary = await self.summarize(
            instruction="Convert decomposition into concise step-by-step roadmap. Include only essential steps and dependencies.",
            context=str(decomposition)
        )

        # PHASE 3: SOLUTION GENERATION & REFINEMENT
        # Generate solutions based on each approach
        symbolic_solution = await self.generate(
            instruction=f"""Implement the symbolic solution approach:
            Approach: {symbolic_result}
            Decomposition Roadmap: {decomposition_summary}
            Classification: {classification}
            
            Requirements:
            - Show complete step-by-step working
            - Box final answer as integer 000-999
            - Include verification against problem constraints
            - If any step uncertain, note assumptions""",
            context=symbolic_result
        )

        # Generate code implementation
        code_solution = await self.programmer(
            instruction=f"""Implement computational solution based on design:
            Design: {code_design}
            Classification: {classification}
            Decomposition: {decomposition_summary}
            
            Requirements:
            - Write complete, self-contained Python code
            - Include verification assertions
            - Handle all edge cases from classification
            - Output must be integer 000-999 (zero-pad if necessary)
            - Return only the final answer as integer""",
            context=code_design
        )

        # Generate stepwise solution following decomposition
        stepwise_solution = await self.generate(
            instruction=f"""Solve problem step-by-step following decomposition roadmap:
            Roadmap: {decomposition_summary}
            Classification: {classification}
            
            Requirements:
            - Solve each subproblem in dependency order
            - Show intermediate results
            - Verify each step before proceeding
            - Final answer must be integer 000-999
            - If any subproblem fails, note and attempt workaround""",
            context=decomposition_summary
        )

        # PHASE 4: VALIDATION & REFINEMENT
        # Revise each solution for errors and clarity
        revised_symbolic = await self.revise(
            instruction=f"""Critically review symbolic solution:
            - Check for arithmetic/logical errors
            - Verify adherence to problem constraints
            - Ensure answer is in 000-999 format
            - Improve clarity of steps if needed
            - Flag any uncertain assumptions
            Classification: {classification}""",
            context=symbolic_solution
        )

        revised_stepwise = await self.revise(
            instruction=f"""Critically review stepwise solution:
            - Verify each subproblem solution
            - Check dependency satisfaction
            - Ensure final answer meets format requirements
            - Improve explanation clarity
            - Note any gaps in reasoning
            Classification: {classification}""",
            context=stepwise_solution
        )

        # PHASE 5: ENSEMBLE SYNTHESIS & FINAL VERIFICATION
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the three solution approaches into final answer:
            Symbolic: {revised_symbolic}
            Code: {code_solution}
            Stepwise: {revised_stepwise}
            Classification: {classification}
            
            Requirements:
            1. Compare results from all three approaches
            2. If all agree, select that answer
            3. If disagreement, identify source of discrepancy and resolve using:
               - Mathematical correctness
               - Adherence to problem constraints
               - Verification against boundary conditions
            4. Final answer MUST be integer 000-999 (zero-pad if necessary)
            5. If still uncertain, default to code solution as most reliable
            6. Output ONLY the 3-digit integer answer""",
            contexts_list=[revised_symbolic, code_solution, revised_stepwise]
        )

        # FINAL FORMATTING & VERIFICATION
        # Ensure answer is properly formatted
        formatted_answer = await self.generate(
            instruction=f"""Format final answer as 3-digit integer:
            Current answer: {final_answer}
            Requirements:
            - Must be exactly 3 digits (000-999)
            - Add leading zeros if necessary
            - Remove any non-digit characters
            - Verify against original problem constraints
            - Output ONLY the 3-digit number""",
            context=final_answer
        )

        # Extract just the 3-digit number using regex as final safeguard
        match = re.search(r'\b(\d{3})\b', formatted_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: extract any number and format to 3 digits
            numbers = re.findall(r'\d+', formatted_answer)
            if numbers:
                num = int(numbers[0]) % 1000  # Ensure in range
                return f"{num:03d}"
            else:
                # Ultimate fallback - return 000 (should never happen)
                return "000"