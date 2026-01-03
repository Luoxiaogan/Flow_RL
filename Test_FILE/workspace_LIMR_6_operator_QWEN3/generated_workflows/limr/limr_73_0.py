# Workflow ID: limr_73_0
# Benchmark: limr
# Data Indices: [271, 266]

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
        import json

        # PHASE 1: META-CLASSIFICATION & PARALLEL INTERPRETATION
        classification = await self.generate(
            instruction="""Perform deep structural analysis of this problem. Identify:
            1. Primary mathematical domain (geometry, number theory, combinatorics, algebra, optimization)
            2. Key constraints (integer solutions, positivity, bounded ranges, diagram dependencies)
            3. Required output format (must be integer 000-999)
            4. Potential solution strategies (analytical, computational, geometric, combinatorial)
            5. Hidden complexities or traps (e.g., extraneous solutions, domain restrictions)
            Output as structured JSON with keys: domain, constraints, strategies, complexities""",
            context=""
        )

        # Generate 3 parallel interpretations using different mathematical lenses
        interpretations = await asyncio.gather(
            self.generate(
                instruction=f"""Interpret this problem through ALGEBRAIC lens:
                - Translate into equations/inequalities
                - Identify variables and their domains
                - Apply symbolic manipulation
                - Focus on exact solutions
                Classification context: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Interpret this problem through GEOMETRIC/SPATIAL lens:
                - If diagram present, extract coordinates, lengths, angles
                - Apply coordinate geometry or vector methods
                - Compute areas, ratios, distances
                - Verify spatial constraints (tangency, perpendicularity)
                Classification context: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Interpret this problem through NUMBER THEORY/COMBINATORIAL lens:
                - Identify integer constraints, divisibility, modular conditions
                - Enumerate cases if bounded
                - Apply counting principles or prime factorization
                - Check for extremal or optimization conditions
                Classification context: {classification}""",
                context=""
            )
        )

        # PHASE 2: HIERARCHICAL DECOMPOSITION & TARGETED SOLVING
        decomposition_tasks = []
        for i, interpretation in enumerate(interpretations):
            decomposition_tasks.append(
                self.decompose(
                    instruction=f"""Decompose this interpretation into atomic subproblems:
                    - Each subproblem must be solvable independently or with specified dependencies
                    - Tag each with mathematical type (equation, count, compute, verify)
                    - Prioritize computational subproblems for Programmer operator
                    - Ensure final step produces integer 000-999
                    Interpretation: {interpretation}""",
                    context=interpretation
                )
            )
        
        decompositions = await asyncio.gather(*decomposition_tasks)

        # Solve each subproblem chain with appropriate operators
        solution_paths = []
        for i, decomposition in enumerate(decompositions):
            path_steps = []
            # Solve subproblems respecting dependencies
            for subproblem in decomposition:
                # Dynamic instruction based on subproblem type
                sub_desc = subproblem['description']
                sub_id = subproblem['id']
                
                if "compute" in sub_desc.lower() or "calculate" in sub_desc.lower():
                    step_result = await self.programmer(
                        instruction=f"""Solve this computational subproblem exactly:
                        {sub_desc}
                        - Use precise arithmetic, no floating point approximations
                        - Return only the numerical result
                        - If multiple answers, return all as list
                        - Must be integer if problem requires it""",
                        context="",
                        max_retries=3
                    )
                else:
                    step_result = await self.generate(
                        instruction=f"""Solve this reasoning subproblem:
                        {sub_desc}
                        - Show logical steps
                        - Justify each assertion
                        - Cross-verify with problem constraints
                        - Final output must be numerical if required""",
                        context=sub_desc
                    )
                    # Adversarial revision for non-computational steps
                    step_result = await self.revise(
                        instruction="""Critique this solution:
                        - Assume it contains an error
                        - Check boundary conditions, integer constraints, and logical consistency
                        - Verify against original problem requirements
                        - Correct any flaws and return improved version""",
                        context=step_result
                    )
                
                path_steps.append({
                    'subproblem_id': sub_id,
                    'result': step_result,
                    'description': sub_desc
                })
            
            solution_paths.append(json.dumps(path_steps))

        # PHASE 3: ADVERSARIAL ENSEMBLE & REFINEMENT
        final_answer = await self.ensemble(
            instruction="""Synthesize solution paths into final answer:
            1. Extract all proposed integer answers (000-999) from each path
            2. For each answer, verify it satisfies:
               - All problem constraints
               - Mathematical consistency
               - No logical gaps
            3. If multiple valid answers, select the one with strongest cross-verification
            4. If no consensus, trigger refinement: decompose conflicting subproblems further
            5. Final output MUST be exactly one integer between 000 and 999
            Format: "ANSWER: XXX" where XXX is the integer""",
            contexts_list=solution_paths
        )

        # PHASE 4: FINAL VERIFICATION & OUTPUT EXTRACTION
        verified_answer = await self.revise(
            instruction="""Final verification:
            - Confirm answer is integer between 000 and 999
            - Ensure no step assumed what wasn't given
            - Check for off-by-one errors or domain violations
            - If answer format incorrect, extract integer from text
            - Output ONLY the integer, no explanation""",
            context=final_answer
        )

        # Extract pure integer (defensive parsing)
        import re
        match = re.search(r'\b(\d{1,3})\b', verified_answer)
        if match:
            return match.group(1).zfill(3)  # Ensure 3-digit format
        else:
            # Fallback: return first 3-digit number found
            numbers = re.findall(r'\d+', verified_answer)
            for num in numbers:
                if len(num) <= 3:
                    return num.zfill(3)
            return "000"  # Ultimate fallback