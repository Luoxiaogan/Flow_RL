# Workflow ID: mgsmbn_62_0
# Benchmark: mgsmbn
# Data Indices: [115]

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

        # PHASE 1: SEMANTIC EXTRACTION & RELATIONSHIP MODELING
        entity_extraction = await self.generate(
            instruction="""You are a Bengali math problem analyst. Extract and structure ALL key components from the problem:

1. ENTITIES: Identify every distinct object, person, or group mentioned (e.g., "কর্মী মৌমাছি", "শিশু মৌমাছি", "রানী মৌমাছি").
2. QUANTITIES: List every numerical value and what it represents (explicit or implicit).
3. RELATIONSHIPS: Map all comparative or functional relationships (e.g., "দ্বিগুণ", "অর্ধেক", "থেকে X বেশি").
4. TARGET: Clearly state what is being asked (the unknown to solve for).
5. CONSTRAINTS: Note any implicit real-world constraints (e.g., whole numbers for countable items, non-negative values).

Format your output as a JSON-like structure with clear section headers. Be exhaustive — missing one relationship can break the solution.""",
            context=""
        )

        # PHASE 2: HIERARCHICAL DECOMPOSITION INTO SUBPROBLEMS
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal, sequentially dependent subproblems. Each subproblem should:

- Represent one logical step toward the final answer
- Have clearly defined inputs (from problem or previous subproblems)
- Have a single, computable output
- Include validation criteria (how to check if the result makes sense)

Prioritize dependency ordering: subproblems that provide inputs to others must come first. For proportional or multi-entity problems, start with base quantities before derived ones.

Example structure for bee problem:
1. Express baby bees in terms of queen bees (given: baby = 2 × queen)
2. Express worker bees in terms of baby bees (given: worker = 2 × baby)
3. Set up total equation: queen + baby + worker = 700
4. Solve for queen bees
5. Back-calculate worker bees (target)

Return as list of dictionaries with 'id', 'description', and 'dependencies'.""",
            context=entity_extraction
        )

        # PHASE 3: PARALLEL SOLUTION STRATEGIES
        async def solve_subproblem(strategy_type, subproblem_desc, prior_context=""):
            strategy_instructions = {
                "algebraic": """Model this subproblem as algebraic equations. Define variables explicitly. Show substitution steps. Solve symbolically before plugging in numbers. Validate dimensional consistency.""",
                "proportional": """Solve using ratio and proportion. Express relationships as fractions or percentages. Use cross-multiplication or scaling factors. Check that proportions preserve original relationships.""",
                "iterative": """Solve by testing reasonable values iteratively. Start with estimates, adjust based on constraints. Stop when all conditions are satisfied. Document each test case."""
            }
            
            return await self.generate(
                instruction=f"""{strategy_instructions[strategy_type]}

Subproblem to solve: {subproblem_desc}

Previous context (if any): {prior_context}

Output ONLY the numerical result or symbolic expression. No explanations.""",
                context=prior_context
            )

        # Execute first subproblem with multiple strategies in parallel
        first_subproblem = decomposition[0]
        strategy_results = await asyncio.gather(
            solve_subproblem("algebraic", first_subproblem['description'], entity_extraction),
            solve_subproblem("proportional", first_subproblem['description'], entity_extraction),
            solve_subproblem("iterative", first_subproblem['description'], entity_extraction)
        )

        # PHASE 4: ENSEMBLE VALIDATION & SELECTION
        first_solution = await self.ensemble(
            instruction="""You are a math solution validator. You have three candidate solutions for the first subproblem. Your tasks:

1. Check each for internal consistency with the original problem's relationships.
2. Verify unit appropriateness (e.g., no fractional bees if context implies whole numbers).
3. Test plausibility (e.g., values shouldn't exceed total given in problem).
4. Select the most consistent solution OR synthesize a new one if all have flaws.

Output ONLY the selected numerical value. No commentary.""",
            contexts_list=strategy_results
        )

        # PHASE 5: SEQUENTIAL CHAIN WITH VALIDATION
        current_solution = first_solution
        solution_chain = [current_solution]
        
        for i, subproblem in enumerate(decomposition[1:], 1):
            # Skip if depends on unsolved subproblems (shouldn't happen with proper decomposition)
            if subproblem['dependencies'] and not all(dep_id in [sp['id'] for sp in decomposition[:i]] for dep_id in subproblem['dependencies'].split(',')):
                continue
                
            # Generate solution using previous results as context
            next_attempt = await self.generate(
                instruction=f"""Solve this subproblem using prior results as inputs:

Subproblem: {subproblem['description']}
Prior solutions: {json.dumps(solution_chain)}

Apply algebraic reasoning. Show substitution steps. Validate that result satisfies:
- Original problem constraints
- Real-world plausibility (whole numbers, positive values, etc.)
- Consistency with previously solved quantities

Output ONLY the numerical result.""",
                context=current_solution
            )
            
            # Validate and revise if necessary
            validation = await self.generate(
                instruction=f"""Critically validate this solution:

Proposed solution: {next_attempt}
Original problem: {self.problem_text}
Previous solutions: {json.dumps(solution_chain)}

Check for:
1. Arithmetic errors
2. Violation of stated relationships
3. Unit/context mismatches
4. Logical inconsistencies

If valid, output "VALID: [value]". If invalid, output "INVALID: [correction]".""",
                context=next_attempt
            )
            
            if "INVALID" in validation:
                current_solution = await self.revise(
                    instruction=f"""Correct the solution based on validation feedback:

Validation result: {validation}
Original subproblem: {subproblem['description']}

Apply necessary corrections. Ensure final answer is numerically precise and contextually appropriate.""",
                    context=next_attempt
                )
            else:
                current_solution = next_attempt
                
            solution_chain.append(current_solution)

        # PHASE 6: FINAL VERIFICATION & OUTPUT
        final_answer = current_solution  # Last in chain should be target value
        
        verification = await self.generate(
            instruction=f"""Perform final verification:

Proposed answer: {final_answer}
Original problem: {self.problem_text}
Full solution chain: {json.dumps(solution_chain)}

Confirm that:
1. Answer directly addresses the question asked
2. All given constraints and relationships are satisfied
3. Units and format match expectations (integer/decimal as appropriate)
4. No calculation steps were skipped or misapplied

If verified, output ONLY the numerical answer. If flawed, output "RETRY" and nothing else.""",
            context=final_answer
        )

        if "RETRY" in verification:
            # Fallback: Direct programmer execution with full context
            final_answer = await self.programmer(
                instruction=f"""Solve this Bengali math problem by generating and executing Python code.

Context: {entity_extraction}
Decomposition: {json.dumps(decomposition)}
Solution chain: {json.dumps(solution_chain)}

Write code that:
- Defines all variables from relationships
- Sets up and solves equations
- Validates answer against total constraints
- Outputs ONLY the final numerical answer

Handle edge cases: ensure integer outputs for countable items, non-negative values, etc.""",
                context=entity_extraction
            )
            
            # Extract just the number from programmer output
            import re
            match = re.search(r'[\d\.]+', final_answer)
            if match:
                final_answer = match.group(0)

        return final_answer