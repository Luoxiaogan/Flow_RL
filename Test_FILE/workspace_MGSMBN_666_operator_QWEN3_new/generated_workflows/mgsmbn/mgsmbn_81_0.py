# Workflow ID: mgsmbn_81_0
# Benchmark: mgsmbn
# Data Indices: [156, 66]

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

        # PHASE 1: LINGUISTIC DECOMPOSITION — Extract entities, quantities, relationships
        entity_extraction = await self.generate(
            instruction="""Thoroughly analyze the Bengali problem text and extract:
            - All numerical values with their units and what they quantify (e.g., '40টি রেস্তোরাঁ' → 40 restaurants)
            - All named entities (people, places, objects) and their roles
            - All actions and verbs indicating mathematical operations (distribute, receive, remain, etc.)
            - Temporal markers (years, months, durations) and their implications
            - Comparative or relational phrases (more than, less than, each, total)
            - Any implicit constraints (non-negative, integer-only, real-world plausibility)
            Format as structured bullet points with clear labels. Resolve pronouns and implicit references explicitly.""",
            context=""
        )

        # PHASE 2: HIERARCHICAL DECOMPOSITION — Break into subproblems with dependencies
        subproblems = await self.decompose(
            instruction=f"""Using the extracted entities and relationships:
            {entity_extraction}

            Decompose this problem into minimal, solvable subproblems. For each subproblem:
            - Clearly state what needs to be computed
            - List required inputs (from text or other subproblems)
            - Specify dependencies (which subproblems must be solved first)
            - Flag any ambiguities or assumptions needed
            Prioritize subproblems that resolve temporal spans, hidden totals, or unit conversions first.
            Ensure the final subproblem computes the requested answer.""",
            context=entity_extraction
        )

        # PHASE 3: PARALLEL SOLUTION GENERATION — Solve independent subproblems concurrently
        async def solve_subproblem(sp):
            desc = sp['description']
            deps = sp.get('dependencies', '').split(',') if sp.get('dependencies') else []
            
            # If no dependencies, solve directly
            if not deps or deps == ['']:
                # Route computational problems to programmer, others to generate
                if any(op in desc.lower() for op in ['calculate', 'compute', 'multiply', 'divide', 'total']):
                    return await self.programmer(
                        instruction=f"""Solve this subproblem with precise Python code:
                        {desc}
                        Use the original problem context and extracted entities. Output only the numerical result.""",
                        context=entity_extraction
                    )
                else:
                    return await self.generate(
                        instruction=f"""Solve step-by-step with explicit reasoning:
                        {desc}
                        Justify each step. Output final numerical answer in boxed format.""",
                        context=entity_extraction
                    )
            else:
                # For dependent subproblems, wait for dependencies (handled by caller)
                return f"PENDING: {desc} (depends on: {deps})"

        # Solve all subproblems in parallel where possible
        subproblem_results = {}
        max_iterations = 3
        unresolved = subproblems.copy()
        
        for _ in range(max_iterations):
            if not unresolved:
                break
                
            current_batch = []
            current_sp_ids = []
            
            for sp in unresolved[:]:
                deps = sp.get('dependencies', '').split(',') if sp.get('dependencies') else []
                if all(dep.strip() in subproblem_results for dep in deps if dep.strip()):
                    current_batch.append(solve_subproblem(sp))
                    current_sp_ids.append(sp['id'])
                    unresolved.remove(sp)
            
            if not current_batch:
                break  # Deadlock
                
            results = await asyncio.gather(*current_batch)
            for sp_id, res in zip(current_sp_ids, results):
                subproblem_results[sp_id] = res

        # PHASE 4: ADVERSARIAL VALIDATION — Parallel verification paths
        final_subproblem_id = subproblems[-1]['id'] if subproblems else "unknown"
        proposed_answer = subproblem_results.get(final_subproblem_id, "No answer generated")

        # Validator 1: Mathematical consistency
        math_validation = await self.generate(
            instruction=f"""Critically validate this answer for mathematical correctness:
            Proposed Answer: {proposed_answer}
            Original Problem: {self.problem_text}
            Extracted Entities: {entity_extraction}
            
            Check:
            - Are all operations applied in correct order?
            - Are units consistent throughout?
            - Are there off-by-one errors (especially in time spans)?
            - Is arithmetic precise (no rounding unless specified)?
            Output "VALID" or "INVALID: [reason]".""",
            context=proposed_answer
        )

        # Validator 2: Contextual plausibility
        context_validation = await self.generate(
            instruction=f"""Validate this answer for real-world plausibility:
            Proposed Answer: {proposed_answer}
            Original Problem: {self.problem_text}
            
            Check:
            - Can the result be negative? (e.g., leftover items, money, people)
            - Are fractional people/objects allowed? (usually not)
            - Does the magnitude make sense? (e.g., 1000 years for a child's age?)
            - Are all constraints from the problem respected?
            Output "PLAUSIBLE" or "IMPLAUSIBLE: [reason]".""",
            context=proposed_answer
        )

        # PHASE 5: ENSEMBLE DECISION — Synthesize validations
        final_answer = await self.ensemble(
            instruction="""Select or synthesize the best answer based on:
            - Mathematical validation result
            - Contextual plausibility result
            - Step-by-step reasoning trace
            
            If both validations pass, return the proposed answer.
            If one fails, attempt to correct it by revising the most likely error.
            If both fail, return the most reasonable estimate with explanation.
            Output ONLY the final numerical answer, nothing else.""",
            contexts_list=[proposed_answer, math_validation, context_validation]
        )

        # PHASE 6: ITERATIVE REFINEMENT (if needed)
        if any(keyword in final_answer.lower() for keyword in ['invalid', 'implausible', 'error', 'uncertain', 'assuming']):
            final_answer = await self.revise(
                instruction=f"""The answer appears uncertain or contains errors:
                {final_answer}
                
                Revise with extreme care:
                - Re-extract key quantities from original problem
                - Re-verify temporal spans (e.g., age 23 to 34 is 11 years, not 12)
                - Re-check unit consistency
                - Ensure no division by zero or negative counts
                Output ONLY the corrected numerical answer.""",
                context=entity_extraction
            )

        # Extract numerical answer using regex (handle various formats)
        match = re.search(r'[\d,]+\.?\d*', final_answer.replace(',', ''))
        if match:
            return float(match.group()) if '.' in match.group() else int(match.group())
        else:
            # Fallback: return 0 if no number found (shouldn't happen in robust workflow)
            return 0