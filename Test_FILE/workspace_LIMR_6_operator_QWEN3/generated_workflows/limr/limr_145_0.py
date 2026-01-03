# Workflow ID: limr_145_0
# Benchmark: limr
# Data Indices: [86, 167]

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

        # STEP 1: Problem Decomposition & Classification
        decomposition = await self.decompose(
            instruction="""Break this problem into atomic subproblems. For each:
            - Identify mathematical domain (algebra, geometry, combinatorics, number theory, etc.)
            - Specify required techniques (equations, proofs, counting, optimization, etc.)
            - List dependencies between subproblems
            - Flag if subproblem requires insight, computation, or both
            Output structured subproblem graph with IDs and dependencies.""",
            context=""
        )

        # STEP 2: Parallel Strategy Generation (Algebraic, Geometric/Combinatorial, Computational)
        strategy_instructions = [
            """Solve using ALGEBRAIC/ANALYTIC approach:
            - Translate problem into equations, functions, or symbolic relationships
            - Use substitutions, eliminations, or transformations
            - Prioritize exact symbolic manipulation over numerical approximation
            - Show all steps leading to final answer""",
            
            """Solve using GEOMETRIC/COMBINATORIAL approach:
            - If geometric: use coordinate systems, vectors, or synthetic properties
            - If combinatorial: use counting principles, probability trees, or case analysis
            - Leverage symmetries, invariants, or recursive structures
            - Visualize if helpful, then formalize""",
            
            """Solve using COMPUTATIONAL approach:
            - Model problem as algorithm or search space
            - Use brute force, iteration, or constraint satisfaction if tractable
            - Prioritize correctness over efficiency (answer is 000-999)
            - Code must be self-contained and verifiable"""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in strategy_instructions]
        )

        # STEP 3: Parallel Adversarial Validation
        validation_tasks = []
        for i, attempt in enumerate(strategy_attempts):
            validation_task = self.revise(
                instruction=f"""ADVERSARIAL VALIDATION for Strategy {i+1}:
                Assume this solution is INCORRECT. Systematically:
                1. Check all algebraic manipulations for sign/operation errors
                2. Verify logical implications (if A then B, but is converse assumed?)
                3. Test edge cases or boundary conditions
                4. Confirm final answer satisfies ALL original constraints
                5. If no error found, explicitly state "VALIDATION PASSED"
                Return concise validation report with confidence score (0-100%)""",
                context=attempt
            )
            validation_tasks.append(validation_task)
        
        validation_reports = await asyncio.gather(*validation_tasks)

        # STEP 4: Ensemble Synthesis with Conflict Resolution
        synthesis = await self.ensemble(
            instruction="""SYNTHESIZE AND RESOLVE:
            1. Extract numerical answer from each strategy (format: 3-digit integer)
            2. Compare answers and validation confidence scores
            3. If ≥2 strategies agree AND have >90% confidence, select consensus
            4. If disagreement:
               a. Identify divergent subproblem from decomposition
               b. Re-solve ONLY that subproblem using Programmer with brute-force
               c. Integrate result into highest-confidence strategy
            5. Output selected answer and brief justification""",
            contexts_list=[f"Strategy {i+1}: {attempt}\nValidation: {report}" 
                          for i, (attempt, report) in enumerate(zip(strategy_attempts, validation_reports))]
        )

        # STEP 5: Iterative Refinement (Max 1 retry if low confidence)
        final_answer = synthesis
        confidence_match = re.search(r'confidence[:\s]+(\d+)%', synthesis.lower())
        current_confidence = int(confidence_match.group(1)) if confidence_match else 0

        if current_confidence < 85:
            # Generate failure analysis and refine decomposition
            failure_analysis = await self.generate(
                instruction=f"""ANALYZE FAILURE:
                Previous confidence: {current_confidence}%
                Why did strategies disagree or lack confidence?
                - Was decomposition incomplete?
                - Were constraints misinterpreted?
                - Is there a non-obvious insight or transformation needed?
                Propose revised decomposition with additional subproblems""",
                context=synthesis
            )
            
            # Revised decomposition and focused re-solve
            revised_decomp = await self.decompose(
                instruction=f"""REVISED DECOMPOSITION based on failure analysis:
                {failure_analysis}
                Add subproblems for: 
                - Alternative formulations (e.g., dual problem, complementary counting)
                - Extreme cases or invariants
                - Dimensional analysis or unit consistency
                Keep dependencies explicit""",
                context=failure_analysis
            )
            
            # Focused computational verification on contentious subproblem
            contentious_id = "SP1"  # Default; in practice, extract from failure analysis
            for sub in revised_decomp:
                if "contentious" in sub['description'].lower() or "critical" in sub['description'].lower():
                    contentious_id = sub['id']
                    break
            
            computational_verification = await self.programmer(
                instruction=f"""BRUTE-FORCE VERIFICATION for subproblem {contentious_id}:
                - Search all possible values in constrained space (000-999 if applicable)
                - Implement explicit constraint checks from original problem
                - Return ONLY the verified integer answer with no explanation""",
                context=f"Subproblem: {contentious_id}\nOriginal Problem: {self.problem_text}"
            )
            
            # Integrate and finalize
            final_answer = await self.ensemble(
                instruction="""INTEGRATE VERIFIED SUBPROBLEM:
                Take computational result and integrate into highest-confidence strategy.
                Output final 3-digit integer answer. If multiple, choose smallest unless context dictates otherwise.""",
                contexts_list=[synthesis, computational_verification]
            )

        # STEP 6: Format Enforcement & Final Validation
        formatted_answer = await self.revise(
            instruction="""FINAL FORMATTING AND VALIDATION:
            1. Extract exactly one integer from the solution
            2. Format as 3-digit string with leading zeros (e.g., 42 → "042")
            3. Verify this answer satisfies ALL original problem constraints
            4. If verification fails, return "000" as fallback
            Output ONLY the 3-digit string, nothing else.""",
            context=final_answer
        )

        # Ensure output is clean 3-digit string
        match = re.search(r'\b\d{3}\b', formatted_answer)
        return match.group(0) if match else "000"