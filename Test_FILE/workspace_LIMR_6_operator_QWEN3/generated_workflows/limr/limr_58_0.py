# Workflow ID: limr_58_0
# Benchmark: limr
# Data Indices: [103, 101]

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

        # PHASE 1: EXPLORATION — Parallel problem analysis and strategy generation
        classification, structural_analysis, strategy_hypotheses = await asyncio.gather(
            self.generate(
                instruction="""Perform deep problem classification:
                1. Identify primary mathematical domain (algebra, geometry, combinatorics, number theory, etc.)
                2. Detect secondary domains or interdisciplinary connections
                3. Classify by required techniques (proof, computation, optimization, counting, etc.)
                4. Estimate solution complexity (low/medium/high) based on steps and insight depth
                5. Flag any ambiguous or underspecified elements
                Format as structured JSON with keys: domain_primary, domain_secondary, technique, complexity, ambiguities""",
                context=""
            ),
            self.generate(
                instruction="""Conduct structural decomposition:
                - Extract all mathematical expressions, constraints, and variables
                - Identify implicit assumptions or hidden symmetries
                - Map relationships between components (dependencies, transformations, equivalences)
                - Highlight potential computational bottlenecks or precision risks
                Present as bullet-pointed analysis with clear section headers""",
                context=""
            ),
            self.generate(
                instruction="""Generate 3 distinct solution strategies:
                Strategy 1: Most straightforward computational approach
                Strategy 2: Elegant mathematical insight or transformation
                Strategy 3: Brute-force or algorithmic fallback
                For each, outline:
                - Key steps and required theorems/tools
                - Potential failure points or edge cases
                - Estimated computational complexity
                - Confidence level (high/medium/low)
                Format as numbered strategies with subsections""",
                context=""
            )
        )

        # PHASE 2: STRATEGY SELECTION & DECOMPOSITION
        selected_strategy = await self.ensemble(
            instruction="""Select the optimal strategy based on:
            - Alignment with problem constraints and precision requirements
            - Computational feasibility and error resistance
            - Elegance and insight depth (prefer non-brute-force when equally viable)
            - Confidence level and risk of edge-case failure
            Justify selection with specific references to classification and structural analysis.
            Output ONLY the selected strategy number (1, 2, or 3) and a one-sentence rationale.""",
            contexts_list=[strategy_hypotheses]
        )

        # Extract selected strategy number
        strategy_num = re.search(r'[1-3]', selected_strategy)
        chosen_strategy = strategy_num.group() if strategy_num else "1"

        # Generate decomposition based on selected strategy
        decomposition_prompt = f"""Decompose the problem using Strategy {chosen_strategy}:
        Original Strategy: {strategy_hypotheses}
        Structural Analysis: {structural_analysis}
        
        Break into atomic, sequentially dependent subproblems. Each subproblem must:
        - Be solvable independently given its dependencies
        - Have clear success criteria (what constitutes a correct solution)
        - Specify required mathematical tools or theorems
        - Flag any precision or rounding requirements
        Return as list of subproblems with 'id', 'description', and 'dependencies' fields."""
        
        subproblems = await self.decompose(
            instruction=decomposition_prompt,
            context=""
        )

        # PHASE 3: PARALLEL SUBPROBLEM EXECUTION
        solutions = {}
        for sp in subproblems:
            dep_ids = [d.strip() for d in sp['dependencies'].split(',') if d.strip()]
            # Wait for dependencies
            if dep_ids:
                await asyncio.gather(*[asyncio.sleep(0) for _ in dep_ids])  # Placeholder for actual dependency wait
            
            # Generate solution attempt
            solution_attempt = await self.generate(
                instruction=f"""Solve subproblem: {sp['description']}
                Context from prior subproblems: {str({k: solutions[k] for k in dep_ids if k in solutions})}
                Requirements: {sp.get('tools', 'Standard mathematical reasoning')}
                Precision: Maintain exact fractions/symbols unless specified otherwise
                Output: Step-by-step solution ending with boxed final answer for this subproblem""",
                context=""
            )
            
            # Verify and revise
            verified_solution = await self.revise(
                instruction="""Critically verify this solution:
                - Check for algebraic errors, logical gaps, or unproven assumptions
                - Validate against problem constraints and prior subproblem results
                - Test edge cases mentioned in structural analysis
                - Ensure precision requirements are met
                If errors found, correct them and explain revisions. If clean, output 'VERIFIED: ' + original""",
                context=solution_attempt
            )
            
            solutions[sp['id']] = verified_solution

        # PHASE 4: SYNTHESIS & FINAL COMPUTATION
        synthesis_context = "\n\n".join([f"Subproblem {k}: {v}" for k, v in solutions.items()])
        
        final_answer_spec = await self.generate(
            instruction=f"""Synthesize subproblem solutions into final answer:
            Subproblem Solutions: {synthesis_context}
            Problem Requirements: {self.problem_text}
            Classification: {classification}
            
            Construct precise computational specification for final answer:
            - Define exact output format (integer, decimal, fraction, etc.)
            - Specify any unit conversions or rounding rules
            - List all variables and their final computed values
            - Outline validation checks against original problem constraints
            Output as structured specification ready for code generation.""",
            context=synthesis_context
        )

        # Generate and execute code
        code_result = await self.programmer(
            instruction=f"""Implement and execute the computational specification:
            Specification: {final_answer_spec}
            Validation Requirements: {classification}
            
            Code must:
            - Use exact arithmetic (fractions, integers) unless decimal specified
            - Include validation assertions against problem constraints
            - Handle edge cases identified in structural analysis
            - Output ONLY the final answer in required format (no explanations)
            If code fails, revise specification and retry (max 3 attempts)""",
            context=final_answer_spec,
            max_retries=3
        )

        # Final verification and formatting
        final_answer = await self.revise(
            instruction="""Extract and format final answer:
            - Must be integer between 000-999 unless problem specifies otherwise
            - Remove all explanatory text, keep only the numeric answer
            - If decimal required, round to specified precision
            - Validate against original problem's answer format requirements
            Output ONLY the final answer in correct format, nothing else.""",
            context=code_result
        )

        return final_answer