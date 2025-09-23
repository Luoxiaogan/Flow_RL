# Workflow ID: mgsmbn_90_0
# Benchmark: mgsmbn
# Data Indices: [29]

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

        # PHASE 1: SEMANTIC ANCHORING — Extract entities, quantities, relationships
        semantic_analysis = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem to extract:
            1. All named entities (people, objects, places)
            2. All numerical values with their units and contextual meaning
            3. Temporal, causal, or proportional relationships (e.g., 'অর্ধেক', 'পরে', 'প্রতি')
            4. Implicit constraints (e.g., non-negative quantities, whole persons)
            5. The explicit question being asked
            Format as structured JSON with keys: entities, quantities, relationships, constraints, question.""",
            context=""
        )

        # PHASE 2: HIERARCHICAL DECOMPOSITION — Break into dependent subproblems
        subproblems = await self.decompose(
            instruction=f"""Decompose the problem into minimal, solvable subproblems based on:
            Semantic Analysis: {semantic_analysis}
            
            Each subproblem must:
            - Be answerable with given or derivable information
            - Specify its dependencies (other subproblem IDs)
            - Include required operations (add, multiply, compare, etc.)
            - Preserve unit consistency
            Return as list of dicts with 'id', 'description', 'dependencies'.""",
            context=semantic_analysis
        )

        # PHASE 3: PARALLEL SOLUTION GENERATION — Solve independent subproblems
        async def solve_subproblem(sp):
            # Check if requires computation
            if any(op in sp['description'] for op in ['calculate', 'compute', 'find value']):
                return await self.programmer(
                    instruction=f"""Solve precisely:
                    Subproblem: {sp['description']}
                    Semantic Context: {semantic_analysis}
                    Use variables from extracted quantities. Show code and result.""",
                    context=semantic_analysis
                )
            else:
                return await self.generate(
                    instruction=f"""Reason step by step:
                    Subproblem: {sp['description']}
                    Use semantic context: {semantic_analysis}
                    Justify your reasoning with extracted relationships.""",
                    context=semantic_analysis
                )

        # Solve all subproblems in dependency order (topological sort implied)
        solutions = {}
        for sp in subproblems:
            # Wait for dependencies
            if sp['dependencies']:
                deps = sp['dependencies'].split(',')
                await asyncio.gather(*[solutions.get(dep_id) for dep_id in deps if dep_id in solutions])
            
            # Solve current subproblem
            solutions[sp['id']] = await solve_subproblem(sp)

        # PHASE 4: SYNTHESIS & VALIDATION — Ensemble with cross-checking
        all_solutions_text = "\n\n".join([f"Subproblem {k}: {v}" for k, v in solutions.items()])
        
        synthesized = await self.ensemble(
            instruction=f"""Synthesize a final answer by:
            1. Cross-validating all subproblem solutions for consistency
            2. Checking unit alignment and real-world plausibility
            3. Resolving contradictions by favoring Programmer outputs or majority logic
            4. Ensuring the answer directly addresses the original question: {semantic_analysis}
            Return ONLY the final numerical answer as a single value.""",
            contexts_list=list(solutions.values())
        )

        # PHASE 5: META-VALIDATION & REFINEMENT — Self-check and revise
        for iteration in range(2):  # Max 2 refinement loops
            validation = await self.generate(
                instruction=f"""Critically evaluate this answer:
                Proposed Answer: {synthesized}
                Original Problem: {self.problem_text}
                Semantic Analysis: {semantic_analysis}
                
                Ask:
                - Are units consistent?
                - Are there hidden steps I missed?
                - Does this violate any implicit constraints?
                - Is the interpretation of ambiguous terms (like 'অর্ধেক') justified?
                If no issues, return 'VALID'. Otherwise, describe the error.""",
                context=synthesized
            )
            
            if "VALID" in validation or "valid" in validation:
                break
            else:
                synthesized = await self.revise(
                    instruction=f"""Revise the answer based on this critique:
                    Critique: {validation}
                    Original Context: {all_solutions_text}
                    Maintain numerical precision and unit consistency.""",
                    context=synthesized
                )

        # FINAL CONFIDENCE CALIBRATION
        final_answer = await self.generate(
            instruction=f"""Extract ONLY the final numerical answer from this text:
            {synthesized}
            If multiple numbers exist, choose the one that answers the original question.
            Return as plain number (integer or decimal) with no units or text.""",
            context=synthesized
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer)
        return cleaned if cleaned else "0"