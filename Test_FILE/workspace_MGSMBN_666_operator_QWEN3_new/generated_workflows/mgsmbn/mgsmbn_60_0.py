# Workflow ID: mgsmbn_60_0
# Benchmark: mgsmbn
# Data Indices: [184]

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

        # Step 1: Parallel extraction of key components with disambiguation
        entity_extraction = await self.generate(
            instruction="""Extract all numerical values, units, named entities, and mathematical relationships from the Bengali problem text. 
            Structure your output as:
            - NUMERICAL VALUES: [list with descriptions]
            - UNITS: [list of units and what they measure]
            - ENTITIES: [people, objects, services mentioned]
            - RELATIONSHIPS: [how values/entities interact mathematically]
            - AMBIGUITIES: [any phrases that could have multiple interpretations]
            Be exhaustive and precise. Preserve Bengali terms but explain their meaning in context.""",
            context=""
        )

        constraint_extraction = await self.generate(
            instruction="""Identify all explicit and implicit constraints in the problem:
            - Physical constraints (e.g., can't have negative items)
            - Logical constraints (e.g., must be integer, must be less than X)
            - Temporal constraints (e.g., sequence of events)
            - Unit consistency requirements
            Format as bullet points with justifications from the text.""",
            context=""
        )

        # Merge extractions and resolve ambiguities
        merged_context = await self.ensemble(
            instruction="""Synthesize the entity extraction and constraint extraction into a unified problem representation.
            Resolve any ambiguities by selecting the most contextually plausible interpretation.
            Flag any remaining uncertainties that might affect the solution.
            Output a structured summary ready for decomposition.""",
            contexts_list=[entity_extraction, constraint_extraction]
        )

        # Step 2: Generate multiple decomposition strategies in parallel
        decomposition_chronological = await self.decompose(
            instruction="""Decompose the problem into subproblems based on chronological order of events.
            Each subproblem should represent a distinct step in the timeline.
            Include dependencies if later steps rely on earlier results.""",
            context=merged_context
        )

        decomposition_mathematical = await self.decompose(
            instruction="""Decompose the problem into subproblems based on mathematical dependencies.
            Group operations that must be performed together.
            Prioritize foundational calculations that feed into others.
            Ignore chronology; focus on computational dependency graph.""",
            context=merged_context
        )

        decomposition_unit_based = await self.decompose(
            instruction="""Decompose the problem by tracking unit transformations.
            Each subproblem should represent a stage where units change or combine.
            Ensure dimensional consistency at each step.
            Highlight any unit conversions required.""",
            context=merged_context
        )

        # Ensemble the decompositions into a consensus roadmap
        subproblems_list = await self.ensemble(
            instruction="""You are given three different decompositions of the same problem. 
            Your task is to merge them into a single, optimal decomposition that:
            - Preserves chronological integrity where relevant
            - Maintains mathematical dependencies
            - Ensures unit consistency throughout
            - Minimizes redundant steps
            - Flags any conflicting interpretations between decompositions
            Output a unified list of subproblems with clear IDs and dependencies.
            If conflicts exist, choose the interpretation most consistent with constraints and real-world plausibility.""",
            contexts_list=[
                str(decomposition_chronological), 
                str(decomposition_mathematical), 
                str(decomposition_unit_based)
            ]
        )

        # Convert to proper list if needed (ensemble might return string representation)
        if isinstance(subproblems_list, str):
            # Attempt to parse as JSON or reconstruct list
            try:
                import json
                subproblems_list = json.loads(subproblems_list)
            except:
                # Fallback: assume it's a list of dicts in string form
                subproblems_list = decomposition_chronological  # Use first as fallback

        # Step 3: Solve each subproblem with parallel code generation and ensemble selection
        async def solve_subproblem(subproblem):
            # Generate multiple code solutions for robustness
            code_attempts = await asyncio.gather(
                self.programmer(
                    instruction=f"""Generate Python code to solve this subproblem: {subproblem['description']}
                    Context: {merged_context}
                    Constraints: {constraint_extraction}
                    Requirements:
                    - Handle units appropriately
                    - Validate against constraints (non-negative, integer if countable, etc.)
                    - Include comments explaining each step
                    - Return only the numerical result""",
                    context="",
                    max_retries=3
                ),
                self.programmer(
                    instruction=f"""Generate ALTERNATE Python code to solve this subproblem: {subproblem['description']}
                    Approach: Use different variable names and calculation order.
                    Context: {merged_context}
                    Constraints: {constraint_extraction}
                    Requirements:
                    - Same as above but with emphasis on unit tracking
                    - Return only the numerical result""",
                    context="",
                    max_retries=3
                )
            )
            
            # Ensemble to select best code result
            best_result = await self.ensemble(
                instruction=f"""Select the most reliable numerical result from these code execution attempts for subproblem: {subproblem['description']}
                Consider:
                - Which result better satisfies problem constraints?
                - Which approach has fewer assumptions?
                - Which is more consistent with unit tracking?
                - If both are valid, prefer the simpler calculation.
                Return ONLY the final numerical value as a string.""",
                contexts_list=code_attempts
            )
            
            # Extract numerical value from result string
            match = re.search(r'[-+]?\d*\.\d+|\d+', best_result)
            if match:
                return float(match.group()) if '.' in match.group() else int(match.group())
            else:
                # Fallback: try to extract from original attempts
                for attempt in code_attempts:
                    match = re.search(r'[-+]?\d*\.\d+|\d+', attempt)
                    if match:
                        return float(match.group()) if '.' in match.group() else int(match.group())
                return 0  # Ultimate fallback

        # Solve subproblems in topological order based on dependencies
        solved_values = {}
        remaining_subproblems = {sp['id']: sp for sp in subproblems_list}
        
        # Simple topological sort (assuming no cycles in elementary problems)
        for _ in range(len(subproblems_list)):
            progress = False
            for sp_id, subproblem in list(remaining_subproblems.items()):
                # Check if all dependencies are satisfied
                deps = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
                deps = [d.strip() for d in deps if d.strip()]
                if all(dep in solved_values for dep in deps):
                    # Solve this subproblem
                    result = await solve_subproblem(subproblem)
                    solved_values[sp_id] = result
                    del remaining_subproblems[sp_id]
                    progress = True
            
            if not progress:
                # Circular dependency or unsolvable - break
                break

        # Step 4: Final answer synthesis and validation
        final_answer_candidates = []
        
        # Candidate 1: Last solved subproblem (assuming it's the final answer)
        if solved_values:
            last_id = list(solved_values.keys())[-1]
            final_answer_candidates.append(str(solved_values[last_id]))
        
        # Candidate 2: Generate explicit final answer from all solved values
        synthesis_context = "\n".join([f"{k}: {v}" for k, v in solved_values.items()])
        explicit_answer = await self.generate(
            instruction=f"""Based on these solved subproblem values:
            {synthesis_context}
            
            And the original problem constraints:
            {constraint_extraction}
            
            What is the final numerical answer to the original question?
            - Ensure it matches the expected unit and format
            - Verify it makes sense in real-world context
            - If multiple interpretations exist, choose the most plausible
            Return ONLY the numerical value.""",
            context=synthesis_context
        )
        final_answer_candidates.append(explicit_answer)

        # Ensemble final answer
        final_answer = await self.ensemble(
            instruction="""Select the most reliable final answer from these candidates.
            Validate against:
            - Original problem question
            - Extracted constraints
            - Real-world plausibility
            - Unit consistency
            Return ONLY the numerical value as a string, nothing else.""",
            contexts_list=final_answer_candidates
        )

        # Extract and clean final numerical value
        match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        if match:
            result = float(match.group()) if '.' in match.group() else int(match.group())
        else:
            # Fallback to first solved value
            result = list(solved_values.values())[0] if solved_values else 0

        return result