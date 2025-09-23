# Workflow ID: mgsmbn_27_0
# Benchmark: mgsmbn
# Data Indices: [25]

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

        # PHASE 1: LINGUISTIC EXTRACTION & ENTITY MAPPING
        entity_extraction = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and extract:
            1. All numerical values with their descriptors (e.g., '110টি মুদ্রা' → value: 110, unit: টি, entity: মুদ্রা)
            2. All named entities (people, objects) and their roles
            3. All comparative or relational phrases (e.g., 'থেকে 30টি বেশি' → '30 more than')
            4. The explicit question being asked (what is unknown?)
            5. Any constraints (e.g., must be integer, non-negative)
            
            Format output as a structured text block with clear section headers:
            [NUMERICAL ENTITIES]
            [RELATIONSHIPS]
            [UNKNOWN VARIABLE]
            [CONSTRAINTS]
            
            Be exhaustive. Preserve original Bengali terms but annotate with English interpretations.""",
            context=""
        )

        # PHASE 2: MATHEMATICAL DECOMPOSITION
        subproblems = await self.decompose(
            instruction="""Based on the extracted entities and relationships, decompose this problem into atomic mathematical subproblems.
            Each subproblem should represent one logical step toward the solution.
            Prioritize:
            - Defining variables for unknowns
            - Translating relationships into equations or expressions
            - Setting up systems of equations if multiple unknowns
            - Identifying sequential operations (do A, then B)
            - Flagging unit conversions or proportional scaling if needed
            
            For each subproblem, specify dependencies (which other subproblems must be solved first).
            Example format:
            id: 1, description: "Let G = number of gold coins, S = number of silver coins", dependencies: ""
            id: 2, description: "From problem: G = S + 30", dependencies: "1"
            id: 3, description: "From problem: G + S = 110", dependencies: "1"
            id: 4, description: "Solve system: substitute G from step 2 into step 3", dependencies: "2,3""",
            context=entity_extraction
        )

        # Handle trivial case: if no decomposition, solve directly
        if len(subproblems) == 0:
            direct_solution = await self.programmer(
                instruction=f"""Solve this problem directly using extracted entities:
                {entity_extraction}
                
                Write Python code that computes the answer. Output only the numerical result.
                Ensure code handles units and constraints mentioned in extraction.""",
                context=entity_extraction
            )
            # Final answer formatting
            final_answer = await self.revise(
                instruction="Extract ONLY the numerical answer from the output. Remove units, text, or explanations. Ensure it's a valid number (int or float).",
                context=direct_solution
            )
            return final_answer.strip()

        # PHASE 3: PARALLEL SUBPROBLEM SOLVING
        async def solve_subproblem(subproblem_desc: str, dep_results: str = "") -> str:
            """Solve one subproblem using appropriate operator based on content"""
            # Check if this is computational or relational
            if any(kw in subproblem_desc.lower() for kw in ["solve", "calculate", "compute", "=", "+", "-", "*", "/"]):
                return await self.programmer(
                    instruction=f"""Execute this mathematical subproblem:
                    {subproblem_desc}
                    
                    Context from dependencies:
                    {dep_results}
                    
                    Write Python code to compute the result. Output intermediate values if needed.
                    Return only the computed value or expression result.""",
                    context=dep_results
                )
            else:
                return await self.generate(
                    instruction=f"""Logically resolve this subproblem:
                    {subproblem_desc}
                    
                    Context from dependencies:
                    {dep_results}
                    
                    Output a clear statement of the result or derived relationship.
                    If numerical, state it explicitly.""",
                    context=dep_results
                )

        # Solve subproblems in dependency order
        solved = {}
        for sub in subproblems:
            deps = [solved[d.strip()] for d in sub['dependencies'].split(',') if d.strip() in solved] if sub['dependencies'] else []
            dep_context = "\n".join(deps) if deps else ""
            
            result = await solve_subproblem(sub['description'], dep_context)
            solved[sub['id']] = f"Subproblem {sub['id']}: {result}"

        # Aggregate all subproblem results
        full_solution_context = "\n".join(solved.values())

        # PHASE 4: PARALLEL VALIDATION & SYNTHESIS
        validation_tasks = [
            self.generate(
                instruction=f"""VALIDATION 1: Unit & Constraint Check
                Problem: {self.problem_text}
                Solution context: {full_solution_context}
                Extracted entities: {entity_extraction}
                
                Verify:
                - All units are consistent (no mixing টাকা with ঘণ্টা)
                - Answer satisfies real-world constraints (non-negative, integer if required)
                - No division by zero or undefined operations
                Output 'VALID' or 'INVALID: [reason]'""",
                context=full_solution_context
            ),
            self.programmer(
                instruction=f"""VALIDATION 2: Alternative Calculation
                Using the same entities and relationships:
                {entity_extraction}
                
                Derive the answer using a DIFFERENT mathematical approach (e.g., if used substitution, now use elimination; if used algebra, now use arithmetic).
                Output only the numerical result.""",
                context=full_solution_context
            ),
            self.generate(
                instruction=f"""VALIDATION 3: Reasonableness Check
                Problem: {self.problem_text}
                Proposed solution: {full_solution_context}
                
                Does this answer make sense in real-world context?
                - Is magnitude reasonable? (e.g., not 1000 coins if total was 110)
                - Does it match the question asked?
                - Are relationships preserved? (e.g., if A is more than B, is result consistent?)
                Output 'REASONABLE' or 'UNREASONABLE: [explanation]'""",
                context=full_solution_context
            )
        ]

        validation_results = await asyncio.gather(*validation_tasks)

        # PHASE 5: ENSEMBLE SYNTHESIS WITH CONSTRAINT-AWARE SELECTION
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the solution considering all validations:
            Primary solution: {full_solution_context}
            Validation 1 (Constraints): {validation_results[0]}
            Validation 2 (Alternative): {validation_results[1]}
            Validation 3 (Reasonableness): {validation_results[2]}
            
            Selection criteria:
            1. If any validation says 'INVALID' or 'UNREASONABLE', reject that path.
            2. Prefer the alternative calculation if primary solution is questionable.
            3. If both methods agree and pass validation, use primary.
            4. Extract ONLY the numerical value that satisfies all constraints.
            5. If decimal, round appropriately based on problem context (e.g., money to 2 decimals, people to integer).
            
            Output ONLY the final numerical answer. No text, no units, no explanation.""",
            contexts_list=[full_solution_context] + validation_results
        )

        # FINAL FORMATTING: Ensure clean numerical output
        cleaned_answer = await self.revise(
            instruction="Strictly extract the numerical value. Remove any non-numeric characters. If multiple numbers, select the one that answers the original question. Convert to float if decimal, int if whole number.",
            context=final_answer
        )

        return cleaned_answer.strip()