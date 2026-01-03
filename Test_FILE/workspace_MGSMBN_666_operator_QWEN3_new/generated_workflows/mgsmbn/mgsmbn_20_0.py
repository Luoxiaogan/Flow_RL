# Workflow ID: mgsmbn_20_0
# Benchmark: mgsmbn
# Data Indices: [183]

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

        # Step 1: Classify problem and detect complexity
        classification = await self.generate(
            instruction="""Analyze this Bengali math problem and classify it:
            1. Problem Type: Is it sequential, proportional, comparative, distribution, rate-based, or simple arithmetic?
            2. Entities: List all objects/people with initial quantities (e.g., "Fire cards: 30")
            3. Events: List all changes (e.g., "loses 8 water cards", "buys 14 grass cards")
            4. Question: What is being asked? (e.g., "probability as percentage")
            5. Complexity Flag: Does it require state tracking over multiple steps? (Yes/No)
            6. Units: What units are involved? (e.g., cards, টাকা, ঘণ্টা)
            7. Constraints: Any real-world constraints? (e.g., no negative cards, probability 0-100%)
            Provide structured response with clear labels for each section.""",
            context=""
        )

        # Step 2: Conditional branching based on complexity
        if "Complexity Flag: No" in classification or "simple arithmetic" in classification.lower():
            # Direct computation path
            solution_attempt = await self.generate(
                instruction=f"""Given this classification:
                {classification}
                
                Directly formulate the mathematical expression needed to solve the problem.
                Show the exact formula using the extracted numbers and relationships.
                Then, state the final answer as a single numerical value.
                If rounding is needed, specify to nearest integer unless otherwise stated.""",
                context=classification
            )
            
            # Extract and compute
            code_result = await self.programmer(
                instruction="""Convert the mathematical expression into executable Python code.
                Ensure proper handling of decimals, rounding, and unit conversions.
                Output only the final numerical result as a float or int.""",
                context=solution_attempt
            )
            
            # Validate and format
            final_answer = await self.revise(
                instruction="""Verify the answer is:
                - Numerically correct (recompute if needed)
                - Properly rounded (to nearest integer unless specified)
                - Within real-world constraints (e.g., 0-100 for percentages, no negatives for counts)
                - Matches the question's requirement (e.g., percentage, total, difference)
                If any issue, correct it. Output only the final number.""",
                context=code_result
            )
            
            return final_answer.strip()

        else:
            # Full state-tracking pipeline for complex problems
            
            # Step 3: Decompose into subproblems
            subproblems = await self.decompose(
                instruction=f"""Break this problem into sequential subproblems based on events:
                Use this classification as guide:
                {classification}
                
                Create subproblems in chronological order:
                1. Initial state (all starting quantities)
                2. After each event (what changes, what stays same)
                3. Final state (all quantities after all events)
                4. Calculation step (what formula to apply on final state)
                5. Answer formatting (rounding, units, constraints)
                
                Each subproblem must:
                - Have a clear ID (e.g., "step1", "step2")
                - Specify dependencies (e.g., "step2 depends on step1")
                - Describe exactly what to compute or extract
                - Reference specific entities and values from classification""",
                context=classification
            )
            
            # Sort subproblems by dependencies (topological sort implied by IDs)
            sorted_subproblems = sorted(subproblems, key=lambda x: int(re.search(r'\d+', x['id']).group()) if re.search(r'\d+', x['id']) else 0)
            
            # Step 4: Solve subproblems sequentially with state tracking
            current_context = classification
            state_tracker = {}
            
            for sp in sorted_subproblems:
                # Generate solution for this subproblem
                sub_solution = await self.generate(
                    instruction=f"""Solve this subproblem:
                    {sp['description']}
                    
                    Current context:
                    {current_context}
                    
                    Instructions:
                    - If initial state: extract and list all starting values
                    - If event: compute new values based on previous state
                    - If calculation: formulate exact mathematical expression
                    - If formatting: apply rounding/constraints
                    - Always update state_tracker with new values
                    - Output should include both reasoning and result""",
                    context=current_context
                )
                
                # Execute computation if needed
                if "calculate" in sp['description'].lower() or "compute" in sp['description'].lower():
                    code_exec = await self.programmer(
                        instruction="""Execute the mathematical operation described.
                        Use values from context. Handle decimals, rounding, and unit conversions.
                        Output the numerical result and updated state.""",
                        context=sub_solution
                    )
                    current_context = code_exec
                else:
                    current_context = sub_solution
                
                # Update state tracker (simplified - in practice, parse and store key values)
                state_tracker[sp['id']] = current_context
            
            # Step 5: Parallel verification - generate 3 interpretations
            verification_branches = await asyncio.gather(
                self.generate(
                    instruction=f"""Verification Branch 1: Re-read original problem and verify if final answer matches narrative.
                    Check: 
                    - All events accounted for?
                    - Units consistent?
                    - Answer within constraints?
                    - Mathematically sound?
                    If error, propose correction.""",
                    context=current_context
                ),
                self.generate(
                    instruction=f"""Verification Branch 2: Plug final answer back into problem. Does it make logical sense?
                    Example: If probability is 33%, with 32 water cards out of 96 total, does 32/96≈33%? 
                    Validate each step backwards. Flag any inconsistency.""",
                    context=current_context
                ),
                self.generate(
                    instruction=f"""Verification Branch 3: Consider alternative interpretations of key phrases.
                    Could any verb or quantity be misread? (e.g., 'loses' vs 'gives away')
                    Would alternative interpretation change answer? If yes, which is most plausible?
                    Justify choice based on context and common sense.""",
                    context=current_context
                )
            )
            
            # Step 6: Ensemble select best verification
            best_verification = await self.ensemble(
                instruction="""Select the most rigorous and correct verification:
                Criteria:
                1. Mathematically accurate
                2. Contextually plausible
                3. Considers edge cases
                4. Aligns with problem constraints
                Output the final validated answer as a single number.""",
                contexts_list=verification_branches
            )
            
            # Step 7: Final revision for formatting
            final_answer = await self.revise(
                instruction="""Ensure final output is:
                - A single numerical value (integer or decimal)
                - Properly rounded (nearest integer unless specified)
                - No units or text (just the number)
                - Within 0-100 for percentages, non-negative for counts
                If not, correct it. Output ONLY the number.""",
                context=best_verification
            )
            
            return final_answer.strip()