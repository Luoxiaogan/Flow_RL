# Workflow ID: mgsmbn_102_0
# Benchmark: mgsmbn
# Data Indices: [100, 8]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # STEP 1: PARALLEL SEMANTIC DECOMPOSITION
        # Generate three independent interpretations of the problem
        decomposition_instructions = [
            """Analyze the problem through a TEMPORAL lens. Identify:
            - All events and their chronological order
            - Initial state, intermediate changes, final state
            - Time markers (when, after, before, initially, finally)
            - How quantities evolve over time
            Structure your response as:
            Temporal Sequence:
            1. [Event 1 with quantities]
            2. [Event 2 with quantities]
            ...
            Goal: [What we need to find]""",
            
            """Analyze the problem through a QUANTITY FLOW lens. Identify:
            - All numerical values and what they represent
            - Units of measurement (টাকা, ঘণ্টা, জিনিস, etc.)
            - Mathematical relationships (ratios, fractions, percentages)
            - What is being added, subtracted, multiplied, divided
            Structure your response as:
            Quantity Map:
            - [Quantity 1]: [Value] [Unit] → [Role]
            - [Quantity 2]: [Value] [Unit] → [Role]
            ...
            Goal: [What we need to find]""",
            
            """Analyze the problem through a CONSTRAINT lens. Identify:
            - Explicit constraints (stated conditions)
            - Implicit constraints (real-world logic: no negative people, integer items)
            - Boundary conditions (minimum/maximum values)
            - What must be true for the answer to make sense
            Structure your response as:
            Constraints:
            - [Constraint 1]: [Description]
            - [Constraint 2]: [Description]
            ...
            Goal: [What we need to find]"""
        ]

        decompositions = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in decomposition_instructions]
        )

        # STEP 2: ENSEMBLE SYNTHESIS OF PROBLEM MODEL
        unified_model = await self.ensemble(
            instruction="""Synthesize the three interpretations into a single, coherent problem model.
            - Identify consensus elements (quantities, events, constraints agreed upon by all)
            - Resolve conflicts by preferring interpretations that:
                a) Maintain unit consistency
                b) Respect chronological order
                c) Satisfy mathematical closure
                d) Align with real-world constraints
            - For each key quantity, state which interpretations agreed on its value and role
            - Explicitly state the unknown we are solving for
            Output format:
            UNIFIED MODEL:
            Entities: [list]
            Initial State: [description]
            Events/Operations: [ordered list]
            Constraints: [list]
            GOAL: [explicit unknown]""",
            contexts_list=decompositions
        )

        # STEP 3: PARALLEL SOLUTION STRATEGY GENERATION
        strategy_instructions = [
            """Develop an ALGEBRAIC solution strategy:
            - Define variables for unknowns
            - Write equations based on relationships
            - Solve step by step
            - Show substitution and simplification
            - Verify solution satisfies all constraints
            Explain each step as if teaching a 5th grader.""",
            
            """Develop a STEP-BY-STEP ARITHMETIC solution strategy:
            - Start from known values
            - Perform operations in chronological/logical order
            - Show intermediate results
            - Track units at each step
            - Verify no step violates constraints
            Explain each calculation clearly.""",
            
            """Develop a SIMULATION strategy:
            - Model the scenario as if acting it out
            - Track state changes after each action
            - Use concrete numbers (not variables)
            - Show before/after states
            - Validate final state matches goal
            Explain like narrating a story with numbers."""
        ]

        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context=unified_model) for instr in strategy_instructions]
        )

        # STEP 4: ENSEMBLE SELECTION OF BEST STRATEGY
        selected_strategy = await self.ensemble(
            instruction="""Select the best solution strategy based on:
            - Clarity of steps (fewest ambiguous operations)
            - Explicit unit tracking
            - Alignment with problem constraints
            - Minimal assumptions
            - Ease of verification
            Justify your selection by comparing all three.
            Then output ONLY the selected strategy text.""",
            contexts_list=strategies
        )

        # STEP 5: ITERATIVE REVISION & VALIDATION
        current_solution = selected_strategy
        max_retries = 2
        answer = None

        for attempt in range(max_retries + 1):
            # Revise with arithmetic verification
            revised = await self.revise(
                instruction="""Audit every numerical calculation:
                - Recompute each arithmetic operation independently
                - Verify unit consistency at each step
                - Check that final answer satisfies all constraints from unified model
                - If any error found, correct it and explain the fix
                - If no errors, output the solution unchanged
                - At the end, extract the FINAL ANSWER as: "FINAL_ANSWER: [number]" """,
                context=current_solution
            )

            # Extract answer
            match = re.search(r"FINAL_ANSWER:\s*([0-9]+\.?[0-9]*)", revised)
            if match:
                answer = match.group(1)
                break
            else:
                # If no answer found, try alternative strategy
                if attempt < max_retries:
                    # Get next best strategy (rotate)
                    alt_strategy = strategies[(attempt + 1) % len(strategies)]
                    current_solution = await self.revise(
                        instruction="Adapt this alternative strategy to fix previous errors",
                        context=alt_strategy
                    )
                else:
                    # Fallback: extract any number from last revision
                    numbers = re.findall(r"[0-9]+\.?[0-9]*", revised)
                    if numbers:
                        answer = numbers[-1]  # last number as fallback
                    else:
                        answer = "0"  # ultimate fallback

        # STEP 6: FINAL VALIDATION & CLEAN OUTPUT
        final_answer = await self.generate(
            instruction=f"""Validate the answer {answer} against the original problem:
            - Does it satisfy all constraints? (positive, integer if required, realistic)
            - Does it match the goal stated in unified model?
            - If not, adjust to nearest valid value and explain why
            Then output ONLY the numerical answer as a string, no units, no explanation.
            Example: "42" or "3.5" """,
            context=unified_model
        )

        # Clean extraction (ensure only number)
        clean_match = re.search(r"([0-9]+\.?[0-9]*)", final_answer)
        if clean_match:
            return clean_match.group(1)
        else:
            return answer  # fallback to previous answer