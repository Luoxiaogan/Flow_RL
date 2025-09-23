# Workflow ID: mgsmbn_63_0
# Benchmark: mgsmbn
# Data Indices: [101, 81]

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

        # PHASE 1: PARALLEL SEMANTIC FRAMING
        # Launch three concurrent analytical perspectives
        entity_extraction, sequence_analysis, archetype_classification = await asyncio.gather(
            self.generate(
                instruction="""Extract all entities, quantities, and units from the Bengali problem.
                Identify:
                - People/agents involved and their actions
                - Objects/items with counts or measurements
                - Numerical values and what they represent
                - Units of measurement (টাকা, ঘণ্টা, জিনিস, etc.)
                - Unknown variable to solve for
                Format as structured bullet points with clear labels.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the temporal and causal sequence of events.
                Determine:
                - What happens first, second, third...
                - Which actions change quantities (add, remove, transfer, consume)
                - Dependencies between events
                - Final state or condition given
                - Initial state (if implied)
                Present as a chronological flow with state changes.""",
                context=""
            ),
            self.generate(
                instruction="""Classify the mathematical archetype of this problem.
                Consider:
                - Is this sequential arithmetic (add/subtract chain)?
                - Proportional reasoning (ratios, percentages, scaling)?
                - Distribution/division (sharing, remainders)?
                - Rate/work/time relationships?
                - Multi-entity tracking with different quantities?
                - Temporal patterns (daily/weekly routines)?
                Also identify if algebraic reasoning (solving for unknown) is required.
                Justify your classification with evidence from the text.""",
                context=""
            )
        )

        # PHASE 2: ENSEMBLE SYNTHESIS INTO UNIFIED MODEL
        unified_model = await self.ensemble(
            instruction="""Synthesize the three analytical perspectives into a single coherent problem model.
            Your unified model must include:
            1. INITIAL STATE: Starting quantities and conditions
            2. EVENT SEQUENCE: Ordered list of quantity-changing actions with mathematical operations
            3. MATHEMATICAL RELATIONSHIPS: Equations or proportionalities connecting knowns and unknowns
            4. TARGET VARIABLE: Clearly state what needs to be solved for
            5. CONSTRAINTS: Real-world limitations (integer values, non-negative quantities, unit consistency)
            6. SOLUTION STRATEGY: Recommended approach (direct calculation, algebraic solving, stepwise simulation)
            Format as a structured JSON-like outline with clear section headers.""",
            contexts_list=[entity_extraction, sequence_analysis, archetype_classification]
        )

        # PHASE 3: CONDITIONAL DECOMPOSITION & STRATEGY SELECTION
        decomposition_needed = await self.generate(
            instruction=f"""Based on the unified model below, determine if decomposition into subproblems is necessary.
            Decomposition is needed if:
            - Multiple unknowns must be solved sequentially
            - Problem involves layered relationships (e.g., rates within rates)
            - Solution requires intermediate variables not directly stated
            - Mathematical archetype is complex (proportional + distribution combined)
            
            Unified Model:
            {unified_model}
            
            Respond with ONLY "YES" or "NO".""",
            context=unified_model
        )

        if "YES" in decomposition_needed.upper():
            # Break down into ordered subproblems
            subproblems = await self.decompose(
                instruction=f"""Decompose this problem into minimal, ordered subproblems.
                Each subproblem should:
                - Be solvable independently once dependencies are met
                - Have a clear mathematical objective
                - Build toward the final answer
                - Include any required unit conversions or constraint checks
                Dependencies must be explicitly stated.
                
                Problem Context:
                {unified_model}""",
                context=unified_model
            )
            
            # Solve subproblems in dependency order
            solutions = {}
            for sp in subproblems:
                # Wait for dependencies
                dep_solutions = "\n".join([f"{dep_id}: {solutions[dep_id]}" for dep_id in sp['dependencies'].split(',') if dep_id.strip() and dep_id in solutions]) if sp['dependencies'] else ""
                
                solution = await self.programmer(
                    instruction=f"""Solve this subproblem using precise computation.
                    Subproblem: {sp['description']}
                    Dependencies resolved: {dep_solutions}
                    Unified Model Context: {unified_model}
                    Show your work step by step. Return only the numerical result with unit if applicable.""",
                    context=f"{unified_model}\n\nDependencies:\n{dep_solutions}"
                )
                solutions[sp['id']] = solution
            
            # Aggregate final answer from last subproblem (assuming last is the target)
            final_computation = solutions[subproblems[-1]['id']] if subproblems else "0"
            
        else:
            # Direct computation path
            final_computation = await self.programmer(
                instruction=f"""Solve the problem directly based on the unified model.
                Model: {unified_model}
                Steps:
                1. Translate the narrative into mathematical equations
                2. Solve for the unknown variable algebraically or arithmetically
                3. Apply all constraints (integer values, non-negative, unit consistency)
                4. Return ONLY the final numerical answer (no units, no explanation)
                Show your symbolic work before computing.""",
                context=unified_model
            )

        # PHASE 4: PLAUSIBILITY VALIDATION
        validated_answer = await self.revise(
            instruction=f"""Validate this answer against real-world plausibility and problem constraints.
            Answer: {final_computation}
            Unified Model: {unified_model}
            
            Check for:
            - Negative quantities where impossible (people, spoons, etc.)
            - Fractional values where integers are required
            - Magnitudes that are absurd (e.g., 10000 spoons in a home)
            - Violation of explicitly stated constraints
            - Unit mismatches
            
            If valid, return the answer unchanged.
            If invalid, explain the issue and compute the corrected answer.
            Return ONLY the final numerical value (corrected if needed).""",
            context=final_computation
        )

        # PHASE 5: REFLECTIVE DEBUGGING (if validation suggests correction)
        if validated_answer != final_computation:
            # Re-solve with corrected constraints
            debugged_solution = await self.programmer(
                instruction=f"""Re-solve the problem incorporating the validation feedback.
                Original Model: {unified_model}
                Validation Feedback: Answer {final_computation} was invalid because {validated_answer} is corrected.
                Apply strict constraint enforcement: integer division, non-negative floors, unit consistency.
                Return ONLY the final numerical answer.""",
                context=unified_model
            )
            final_answer = debugged_solution
        else:
            final_answer = validated_answer

        # Extract clean numerical answer (remove any residual text)
        # Use regex to find first number (integer or decimal)
        match = re.search(r'(-?\d*\.?\d+)', final_answer.replace(',', ''))
        if match:
            return match.group(1)
        else:
            # Fallback: return as-is if no number found (shouldn't happen)
            return final_answer.strip()