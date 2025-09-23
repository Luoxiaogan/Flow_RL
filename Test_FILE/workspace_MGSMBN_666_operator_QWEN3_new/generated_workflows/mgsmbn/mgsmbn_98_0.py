# Workflow ID: mgsmbn_98_0
# Benchmark: mgsmbn
# Data Indices: [195, 148]

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

        # Step 1: Deep semantic parsing - extract actors, actions, resources, constraints
        semantic_parse = await self.generate(
            instruction="""Perform deep semantic analysis of the Bengali word problem. Identify:
            - All entities (people, objects, resources) and their roles
            - Actions performed and their temporal sequence
            - Quantities with their units and relationships
            - Explicit and implicit constraints (e.g., 'cannot exceed', 'must be whole number')
            - What is being asked (the unknown)
            Format as structured markdown with clear sections.""",
            context=""
        )

        # Step 2: Normalize and fill in elliptical references
        canonical_form = await self.summarize(
            instruction="""Convert the semantic parse into a canonical problem statement:
            - Fill in any omitted subjects/objects using context
            - Make all relationships explicit (e.g., 'A is twice B' → A = 2×B)
            - State all assumptions made during filling
            - Preserve units and temporal markers
            Output should be a self-contained, unambiguous problem description.""",
            context=semantic_parse
        )

        # Step 3: Classify problem type to determine solution strategy
        problem_type = await self.generate(
            instruction="""Classify this problem into exactly one primary type:
            [Sequential Resource Tracking, Probability/Combinatorics, Proportional Reasoning, Distribution/Allocation, Comparison/Difference]
            Justify your classification with specific evidence from the problem.
            Then recommend the optimal solution approach: Algebraic Formulation, Step-by-Step Simulation, Combinatorial Enumeration, or Direct Calculation.""",
            context=canonical_form
        )

        # Step 4: Parallel solution generation - algebraic vs simulation approaches
        algebraic_approach = await self.generate(
            instruction="""Formulate this problem as a system of algebraic equations or expressions.
            - Define variables for unknowns
            - Write equations representing all relationships
            - Include unit tracking as dimensional analysis
            - Do not solve yet—just set up the mathematical model.""",
            context=canonical_form
        )

        simulation_approach = await self.generate(
            instruction="""Model this problem as a step-by-step chronological simulation:
            - Break into discrete time steps or events
            - Track state changes (quantities, conditions) at each step
            - Include validation checks at each transition
            - Output should be a narrative of state evolution leading to final answer.""",
            context=canonical_form
        )

        # Step 5: Ensemble best approach based on problem type and complexity
        selected_approach = await self.ensemble(
            instruction=f"""Given the problem classification: {problem_type}
            Compare these two solution approaches:
            1. Algebraic Formulation: {algebraic_approach}
            2. Step-by-Step Simulation: {simulation_approach}
            
            Select the approach that is:
            - Most aligned with the problem type
            - Requires fewest assumptions
            - Most straightforward to compute
            - Most resistant to off-by-one or unit errors
            Justify your selection and output ONLY the selected approach text.""",
            contexts_list=[algebraic_approach, simulation_approach]
        )

        # Step 6: Decompose into executable subproblems
        subproblems = await self.decompose(
            instruction="""Break the selected approach into executable subproblems:
            - Each subproblem should be independently solvable
            - Specify input dependencies between subproblems
            - Include unit consistency checks as separate subproblems if needed
            - Output should be machine-readable with clear IDs and dependencies.""",
            context=selected_approach
        )

        # Step 7: Execute subproblems in dependency order
        solutions = {}
        for subproblem in sorted(subproblems, key=lambda x: len(x.get('dependencies', '').split(',')) if x.get('dependencies') else 0):
            sub_id = subproblem['id']
            deps = [solutions[dep_id.strip()] for dep_id in subproblem.get('dependencies', '').split(',') if dep_id.strip() in solutions] if subproblem.get('dependencies') else []
            dep_context = "\n".join(deps) if deps else ""
            
            code_solution = await self.programmer(
                instruction=f"""Solve this subproblem using Python:
                {subproblem['description']}
                
                Context from dependencies:
                {dep_context}
                
                Requirements:
                - Include unit assertions (e.g., assert value >= 0)
                - Handle edge cases mentioned in original problem
                - Output only the numerical result with appropriate precision
                - If error occurs, return 'ERROR' and brief reason""",
                context=dep_context,
                max_retries=2
            )
            solutions[sub_id] = code_solution

        # Step 8: Validate final answer against real-world constraints
        final_answer_raw = solutions.get('final', solutions[list(solutions.keys())[-1]] if solutions else "")
        validated_answer = await self.revise(
            instruction="""Validate this numerical answer against real-world plausibility:
            - Check for negative quantities where impossible
            - Verify fractional results against entity types (e.g., people must be integers)
            - Confirm unit consistency with original problem
            - Assess magnitude reasonableness (e.g., phone minutes can't exceed 10000 in a month)
            If any issue found, propose corrected calculation. Otherwise, return the answer unchanged.
            Output ONLY the final validated number.""",
            context=final_answer_raw
        )

        # Step 9: Extract clean numerical answer
        clean_answer = await self.generate(
            instruction="""Extract ONLY the final numerical answer from the validated result.
            - Remove all units, explanations, and formatting
            - Round to precision implied by problem (integer if all inputs integer, etc.)
            - If answer is decimal, use minimal necessary precision
            - Output must be a single number string (e.g., "250", "3.14")""",
            context=validated_answer
        )

        # Final output - ensure it's a clean number
        match = re.search(r'[-+]?\d*\.?\d+', clean_answer)
        return match.group(0) if match else "0"