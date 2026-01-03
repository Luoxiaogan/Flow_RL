# Workflow ID: mgsmbn_47_0
# Benchmark: mgsmbn
# Data Indices: [93]

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

        # STEP 1: Extract structured problem representation from Bengali text
        problem_structure = await self.generate(
            instruction="""Perform deep semantic extraction of this Bengali math word problem. Identify and categorize:

1. ENTITIES: People, objects, or groups mentioned (e.g., 'জন', 'সন্তান', 'জুতো')
2. QUANTITIES: All numerical values with their associated units and what they measure (e.g., '3 সন্তান', '2 জোড়া', '$60 প্রতি জোড়া')
3. RELATIONSHIPS: How quantities relate (e.g., 'প্রত্যেকের জন্য' implies multiplication across entities)
4. OPERATIONS: Explicit or implicit mathematical operations (addition, multiplication, division, etc.)
5. CONSTRAINTS: Real-world limitations (e.g., whole numbers for people, non-negative values)
6. TARGET: What is being asked for (the unknown to solve)

Format as JSON with keys: entities, quantities, relationships, operations, constraints, target. Be exhaustive and precise.""",
            context=""
        )

        # STEP 2: Classify problem type to determine solution strategy
        problem_classification = await self.generate(
            instruction=f"""Based on the structured problem representation below, classify this problem:

{problem_structure}

Choose primary type from: 
- DIRECT_ARITHMETIC (simple calculations with clear operations)
- PROPORTIONAL (ratios, percentages, scaling)
- ALGEBRAIC (requires solving for unknowns with equations)
- MULTI_STEP (requires sequential operations with dependencies)
- COMPARISON (finding differences or relative quantities)
- DISTRIBUTION (dividing or sharing quantities)

Also identify:
- Complexity level (1-5, 5 being most complex)
- Number of distinct calculation steps required
- Whether unit conversion is needed
- Whether intermediate variables are required

Output as JSON with keys: type, complexity, steps, unit_conversion_needed, intermediate_variables_needed""",
            context=problem_structure
        )

        # STEP 3: Generate multiple solution approaches in parallel
        classification_data = json.loads(problem_classification)
        problem_type = classification_data["type"]

        # Dynamically construct approach instructions based on problem type
        approach_instructions = []
        
        if problem_type == "DIRECT_ARITHMETIC":
            approach_instructions.extend([
                "Solve using direct arithmetic operations. Show step-by-step calculation with units tracked throughout.",
                "Solve by creating a unit analysis table, ensuring dimensional consistency at each step.",
                "Solve by breaking into smallest possible operations and aggregating results."
            ])
        elif problem_type == "PROPORTIONAL":
            approach_instructions.extend([
                "Solve using ratio and proportion formulas. Set up proportion equations and solve algebraically.",
                "Solve using unit rate method: find cost/quantity per unit then scale to required quantity.",
                "Solve using percentage/fraction conversion if applicable, showing all conversion steps."
            ])
        elif problem_type == "ALGEBRAIC":
            approach_instructions.extend([
                "Solve by defining variables for unknowns, setting up equations, and solving systematically.",
                "Solve using substitution method if multiple variables are involved.",
                "Solve by creating a system of equations and using elimination method."
            ])
        elif problem_type == "MULTI_STEP":
            approach_instructions.extend([
                "Solve by decomposing into chronological steps and solving sequentially.",
                "Solve by identifying dependencies between operations and building calculation tree.",
                "Solve by working backwards from target to given values."
            ])
        else:  # Default comprehensive approach
            approach_instructions.extend([
                "Solve using most appropriate mathematical method for this problem type. Show all steps.",
                "Solve by creating detailed mathematical model with variables and equations.",
                "Solve by breaking into subproblems and solving each independently then combining."
            ])

        # Generate multiple solution attempts in parallel
        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""{instr}

Use the following structured problem representation as reference:
{problem_structure}

Show all work clearly. Track units throughout. Verify intermediate results make sense in context.
Final answer must be a single numerical value matching the target specified in the problem.""",
                context=problem_structure
            ) for instr in approach_instructions]
        )

        # STEP 4: Extract mathematical models from solution attempts
        models = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract the core mathematical model from this solution attempt:

{attempt}

Identify:
- Variables used (if any)
- Equations or formulas applied
- Step-by-step calculation sequence
- Unit handling at each step
- Final numerical answer

Format as JSON with keys: variables, equations, steps, units, final_answer""",
                context=attempt
            ) for attempt in solution_attempts]
        )

        # STEP 5: Execute mathematical models via Programmer
        code_results = await asyncio.gather(
            *[self.programmer(
                instruction=f"""Execute this mathematical model:

{model}

Generate Python code that:
1. Defines all necessary variables
2. Performs calculations in specified sequence
3. Tracks and validates units at each step
4. Outputs only the final numerical answer
5. Includes assertions to validate against problem constraints

If any step produces invalid result (negative people, fractional shoes, etc.), raise ValueError with explanation.""",
                context=model
            ) for model in models]
        )

        # STEP 6: Ensemble - select best answer from parallel executions
        final_answer = await self.ensemble(
            instruction="""Select the most accurate and reliable numerical answer from the following candidates:

Evaluate based on:
1. Mathematical correctness (does the code execute without error?)
2. Unit consistency (are units tracked and validated throughout?)
3. Contextual plausibility (does answer make sense in real-world context?)
4. Alignment with problem constraints (does it respect implicit limitations?)
5. Step-by-step validity (are intermediate results reasonable?)

If multiple answers are valid, select the one with most rigorous unit handling and constraint validation.
If all answers have issues, select the least problematic and note the concern.

Output ONLY the final numerical answer as a single number (integer or decimal).""",
            contexts_list=code_results
        )

        # STEP 7: Final verification and cleanup
        verified_answer = await self.revise(
            instruction=f"""Verify this final answer: {final_answer}

Check:
1. Does it match the problem's requested target?
2. Is it in correct units (if specified)?
3. Is it reasonable given problem context? (e.g., not negative when impossible, not fractional when should be whole)
4. Does it align with the structured problem representation?

If any issue found, correct it. Otherwise, return the answer unchanged.

Output ONLY the final numerical value.""",
            context=final_answer
        )

        return verified_answer