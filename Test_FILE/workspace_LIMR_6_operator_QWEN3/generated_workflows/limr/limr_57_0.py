# Workflow ID: limr_57_0
# Benchmark: limr
# Data Indices: [274, 172]

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

        # === PHASE 1: EXPLORATORY DIAGNOSIS & STRATEGY SYNTHESIS ===
        
        # Generate parallel analytical perspectives
        perspectives = await asyncio.gather(
            self.generate(
                instruction="""Analyze this problem from an ALGEBRAIC perspective:
                - Identify all variables, functions, and equations
                - Look for symmetries, invariants, or functional equations
                - Suggest substitutions or transformations that could simplify
                - Note any constraints or domain restrictions
                Format as a structured bullet-point analysis.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from a COMBINATORIAL/PROBABILISTIC perspective:
                - Identify counting elements, sample spaces, events
                - Look for overcounting risks, independence assumptions
                - Consider complementary counting or recursive structures
                - Note any symmetry or equivalence classes
                Format as a structured bullet-point analysis.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from a NUMBER THEORETIC/GEOMETRIC perspective:
                - Identify any modular arithmetic, divisibility, or prime structure
                - For geometry: coordinate systems, transformations, invariants
                - Look for Diophantine constraints or geometric symmetries
                - Note any bounds, extremal conditions, or discrete structures
                Format as a structured bullet-point analysis.""",
                context=""
            )
        )

        # Refine each perspective for clarity and depth
        refined_perspectives = await asyncio.gather(
            *[self.revise(
                instruction=f"""Improve this analysis:
                - Add missing mathematical details
                - Clarify ambiguous statements
                - Strengthen logical connections
                - Flag any assumptions being made
                - Ensure mathematical notation is precise""",
                context=p
            ) for p in perspectives]
        )

        # Synthesize into unified problem understanding
        problem_map = await self.ensemble(
            instruction="""Synthesize these analyses into a SINGLE coherent problem map:
            - Identify the PRIMARY mathematical domain(s) involved
            - List all key quantities, relationships, and constraints
            - Highlight any non-obvious insights or transformations needed
            - Propose a high-level solution strategy integrating the best elements
            - Flag any potential pitfalls or edge cases
            Output as a well-structured markdown document with clear sections.""",
            contexts_list=refined_perspectives
        )

        # Decompose into executable subproblems
        subproblems = await self.decompose(
            instruction="""Break this problem into minimal, executable subproblems:
            - Each subproblem should be solvable independently if dependencies are met
            - Specify input requirements and expected output format
            - Order by dependency: which subproblems must be solved first?
            - Include at least one computational subproblem if applicable
            - For proof-based steps, frame as 'verify that X implies Y'
            Return as a list of subproblem dictionaries with 'id', 'description', 'dependencies'.""",
            context=problem_map
        )

        # === PHASE 2: ADAPTIVE EXECUTION & VERIFICATION ===
        
        solved_subproblems = {}
        
        # Process subproblems in dependency order
        for subproblem in subproblems:
            sub_id = subproblem['id']
            description = subproblem['description']
            deps = subproblem.get('dependencies', "").split(",") if subproblem.get('dependencies') else []
            
            # Wait for dependencies
            dep_context = "\n".join([f"Subproblem {dep}: {solved_subproblems.get(dep, 'UNSOLVED')}" 
                                   for dep in deps if dep.strip()])
            
            full_context = f"""DEPENDENCIES RESOLVED:
{dep_context}

CURRENT SUBPROBLEM:
{description}

GLOBAL PROBLEM CONTEXT:
{problem_map}"""

            # Classify subproblem type for routing
            subproblem_type = await self.generate(
                instruction="""Classify this subproblem for optimal solving strategy:
                Choose ONE primary type:
                - COMPUTATIONAL: Requires calculation, iteration, or algorithm
                - ALGEBRAIC: Requires symbolic manipulation, equation solving
                - COMBINATORIAL: Requires counting, probability, case analysis
                - GEOMETRIC: Requires spatial reasoning, coordinate work
                - PROOF: Requires logical deduction, verification, induction
                - OTHER: Doesn't fit above (explain)

                Then recommend the BEST solving approach and WHY.
                Format: "TYPE: [type] | APPROACH: [description] | REASON: [justification]".""",
                context=full_context
            )

            # Route to appropriate solver with dynamic instruction
            if "COMPUTATIONAL" in subproblem_type.upper():
                solution = await self.programmer(
                    instruction=f"""Solve this computational subproblem:
                    {description}

                    CONTEXT:
                    {full_context}

                    INSTRUCTIONS:
                    - Write efficient, well-commented Python code
                    - Include input validation and edge case handling
                    - Use exact arithmetic (no floating point unless necessary)
                    - Return only the final answer in the required format
                    - Include assert statements to verify correctness
                    - If multiple answers possible, return all then select based on global constraints""",
                    context=full_context,
                    max_retries=3
                )
            else:
                # Non-computational: generate + revise loop
                solution_attempt = await self.generate(
                    instruction=f"""Solve this subproblem with rigorous mathematical reasoning:
                    {description}

                    CONTEXT:
                    {full_context}

                    INSTRUCTIONS:
                    - Show all steps clearly
                    - Justify each non-trivial assertion
                    - Use proper mathematical notation
                    - Consider edge cases and special conditions
                    - Box the final answer for this subproblem""",
                    context=full_context
                )
                
                # Verify and refine
                solution = await self.revise(
                    instruction=f"""Verify and improve this solution:
                    - Check for logical gaps or calculation errors
                    - Ensure alignment with global problem constraints
                    - Improve clarity and mathematical rigor
                    - Confirm the answer format is correct
                    - If errors found, correct them and explain the fix""",
                    context=solution_attempt
                )

            # Store result
            solved_subproblems[sub_id] = solution

        # === PHASE 3: CONSENSUS REFINEMENT & ANSWER EXTRACTION ===
        
        # Gather all subproblem solutions
        all_solutions_text = "\n\n".join([f"Subproblem {k}: {v}" for k, v in solved_subproblems.items()])
        
        # Synthesize final answer
        final_answer_draft = await self.ensemble(
            instruction=f"""Synthesize a FINAL ANSWER from all subproblem solutions:
            - The answer must be an integer between 000 and 999
            - Trace how subproblem results combine to form the final answer
            - Resolve any contradictions by tracing back to root causes
            - If multiple candidate answers exist, select the one most consistent with ALL constraints
            - Present ONLY the final three-digit integer (zero-padded if necessary)
            - Do NOT include units, explanations, or markdown formatting""",
            contexts_list=[all_solutions_text, problem_map]
        )

        # Format and validate final answer
        final_answer = await self.revise(
            instruction="""Ensure this is a valid final answer:
            - Must be exactly three digits (000-999)
            - Must be an integer (no decimals, fractions, or variables)
            - Must be derived from the problem's constraints
            - If not in correct format, derive the correct integer answer
            - Output ONLY the three-digit number, nothing else""",
            context=final_answer_draft
        )

        # Extract just the number using regex to ensure cleanliness
        match = re.search(r'\b\d{3}\b', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: try to extract any number and format it
            numbers = re.findall(r'\d+', final_answer)
            if numbers:
                num = int(numbers[0]) % 1000  # Ensure in range
                return f"{num:03d}"
            else:
                # Ultimate fallback - indicate failure gracefully
                return "000"