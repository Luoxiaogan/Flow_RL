# Workflow ID: mgsmbn_3_0
# Benchmark: mgsmbn
# Data Indices: [38, 126]

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

        # STEP 1: SEMANTIC DECOMPOSITION
        decomposition = await self.decompose(
            instruction="""Thoroughly decompose this Bengali word problem into its fundamental components. For each component, identify:
            1. ENTITIES: All objects, people, or quantities mentioned (e.g., "floors", "monkeys", "bananas"). For each, specify its unit (টাকা, ঘণ্টা, জিনিস, etc.) and initial value if given.
            2. ACTIONS: What operations or changes occur (e.g., "orders every 2 months", "3/4 occupied"). Specify timing, frequency, and direction (increase/decrease).
            3. CONSTRAINTS: Explicit limits (e.g., "can't be negative") and implicit real-world constraints (e.g., "must be integer for people").
            4. GOAL: The exact unknown to solve for, including expected unit and format.
            5. DEPENDENCIES: Which components must be calculated before others.
            
            Output as a numbered list of subproblems. Each subproblem must have:
            - id: Unique identifier (e.g., "entity_1", "action_2")
            - description: Clear natural language description
            - dependencies: Comma-separated list of prerequisite subproblem IDs (or "none" if independent)
            
            Prioritize granularity — break complex actions into atomic steps.""",
            context=""
        )

        # STEP 2: PARALLEL MODELING PATHS (DIAMOND PATTERN)
        # Three independent modeling approaches to capture different reasoning dimensions
        modeling_tasks = [
            # PATH 1: MATHEMATICAL FORMALIZATION
            self.generate(
                instruction=f"""Based on this decomposition:
                {json.dumps(decomposition, indent=2, ensure_ascii=False)}
                
                Create a rigorous mathematical model:
                - Translate narrative into equations or expressions
                - Define variables for unknowns with clear symbols
                - Specify order of operations
                - Highlight any algebraic manipulations needed
                - Do NOT compute yet — output only the symbolic model""",
                context=""
            ),
            
            # PATH 2: UNIT-AWARE SIMULATION
            self.generate(
                instruction=f"""Based on this decomposition:
                {json.dumps(decomposition, indent=2, ensure_ascii=False)}
                
                Construct a unit-tracking simulation:
                - Map each entity to its physical unit (টাকা, ঘণ্টা, জিনিস, etc.)
                - Verify dimensional consistency at each operation
                - Flag any unit mismatches or conversions needed
                - Outline step-by-step state changes with units preserved
                - Output as a chronological sequence of state transitions""",
                context=""
            ),
            
            # PATH 3: NARRATIVE CHRONOLOGY
            self.generate(
                instruction=f"""Based on this decomposition:
                {json.dumps(decomposition, indent=2, ensure_ascii=False)}
                
                Reconstruct the problem as a timeline of events:
                - Order all actions chronologically
                - For each event, specify: what changes, by how much, and under what conditions
                - Identify causal relationships between events
                - Highlight any hidden steps implied by the narrative
                - Output as a numbered sequence of temporal steps""",
                context=""
            )
        ]
        
        # Execute all modeling paths in parallel
        math_model, unit_model, narrative_model = await asyncio.gather(*modeling_tasks)

        # STEP 3: PARALLEL COMPUTATION (PROGRAMMER OPERATOR FOR EACH PATH)
        computation_tasks = [
            # Compute from mathematical model
            self.programmer(
                instruction=f"""Execute this mathematical model:
                {math_model}
                
                Generate Python code that:
                - Uses descriptive variable names matching entities
                - Includes assertions for constraints (e.g., assert x >= 0)
                - Outputs ONLY the final numerical answer (no text)
                - Handles fractions/decimals precisely
                - Double-checks order of operations""",
                context=math_model
            ),
            
            # Compute from unit-aware simulation
            self.programmer(
                instruction=f"""Execute this unit-aware simulation:
                {unit_model}
                
                Generate Python code that:
                - Tracks units explicitly in variable names (e.g., bananas_count, months_duration)
                - Validates unit consistency at each step
                - Converts units only when necessary and justified
                - Outputs ONLY the final numerical answer
                - Includes sanity checks (e.g., integer constraints for countable items)""",
                context=unit_model
            ),
            
            # Compute from narrative chronology
            self.programmer(
                instruction=f"""Execute this narrative chronology:
                {narrative_model}
                
                Generate Python code that:
                - Simulates events in chronological order
                - Updates state variables after each event
                - Logs intermediate values for verification
                - Outputs ONLY the final numerical answer
                - Validates against real-world plausibility at each step""",
                context=narrative_model
            )
        ]
        
        # Execute all computations in parallel
        math_result, unit_result, narrative_result = await asyncio.gather(*computation_tasks)

        # STEP 4: ENSEMBLE SYNTHESIS WITH META-REASONING
        final_answer = await self.ensemble(
            instruction=f"""Synthesize these three computational results:
            Mathematical Model Result: {math_result}
            Unit-Aware Simulation Result: {unit_result}
            Narrative Chronology Result: {narrative_result}
            
            Perform meta-analysis:
            1. Compare numerical outputs — do they agree?
            2. For each result, evaluate:
               - Consistency with original problem narrative
               - Unit/dimensional correctness
               - Adherence to real-world constraints
               - Robustness of assumptions
            3. If results differ, identify which model best handles edge cases and why
            4. If all agree, verify against decomposition's goal specification
            5. Output ONLY the final numerical answer (no explanation)
            
            In case of disagreement, prioritize the model that:
            - Best preserves unit consistency
            - Most faithfully follows chronological narrative
            - Has strongest constraint validation""",
            contexts_list=[math_result, unit_result, narrative_result]
        )

        # STEP 5: SANITY CHECK & REVISION (ITERATIVE LOOP)
        for attempt in range(2):  # Max 2 revision attempts
            sanity_check = await self.generate(
                instruction=f"""Perform final sanity check on answer: {final_answer}
                
                Verify against:
                1. Original problem's real-world context — is this answer plausible?
                2. Magnitude — is it within expected range? (e.g., not millions for small apartment)
                3. Unit — does it match the required output unit?
                4. Format — is it numerical (integer/decimal) as required?
                
                If any issue found, specify exactly what's wrong and how to fix.
                If perfect, output ONLY "VALID".""",
                context=final_answer
            )
            
            if "VALID" in sanity_check:
                break
            else:
                # Revise using feedback
                final_answer = await self.revise(
                    instruction=f"""Revise the answer based on this feedback:
                    {sanity_check}
                    
                    Adjust calculation, constraints, or assumptions as needed.
                    Output ONLY the revised numerical answer.""",
                    context=final_answer
                )

        return final_answer