# Workflow ID: mgsmbn_43_0
# Benchmark: mgsmbn
# Data Indices: [64, 123]

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

        # Step 1: Parallel Fork - Semantic Decomposition + Unit Mapping
        decomposition_task = self.decompose(
            instruction="""Break down the Bengali word problem into atomic semantic frames. Each frame must include:
            - Actor (who is performing the action)
            - Action (what is being done: add, remove, compare, distribute, etc.)
            - Object (what is being acted upon, with unit if specified)
            - Quantity or Change (exact number, or relative like 'twice', 'half', '5 more than')
            - Temporal Order (if actions are sequential)
            If any quantity is ambiguous (e.g., 'কয়েকটি', 'প্রায়'), explicitly flag it as 'AMBIGUOUS'.
            Output as a numbered list of structured frames.""",
            context=""
        )

        unit_mapping_task = self.generate(
            instruction="""Extract all units and numerical relationships from the problem. For each number:
            - Identify what it quantifies (e.g., '25টি গোলাপ' → 25 roses)
            - Note the unit (টাকা, ঘণ্টা, জিনিস, etc.)
            - Flag if unit conversion is needed (e.g., dollars to cents)
            - Map relationships: 'প্রতিটি' → per unit, 'মোট' → total, 'অর্ধেক' → divide by 2
            Output as a structured dictionary: {number: {description, unit, conversion_needed, relationship}}""",
            context=""
        )

        decomposition, unit_mapping = await asyncio.gather(decomposition_task, unit_mapping_task)

        # Step 2: Generate Mathematical Skeleton
        skeleton = await self.generate(
            instruction=f"""Based on the semantic decomposition and unit mapping, generate a step-by-step mathematical skeleton.
            Decomposition: {decomposition}
            Unit Mapping: {unit_mapping}
            
            Rules:
            - Translate each semantic frame into a mathematical operation (+, -, ×, ÷, =, etc.)
            - Use descriptive variable names (e.g., total_thorns, cookie_price)
            - If 'AMBIGUOUS' is flagged, propose 2-3 plausible interpretations (e.g., 'কয়েকটি' → 3, 5, or 7)
            - Include unit conversions explicitly (e.g., dollars = cents / 100)
            - Sequence operations chronologically if time-based
            Output as pseudo-code with comments explaining each step.""",
            context=f"{decomposition}\n\n{unit_mapping}"
        )

        # Step 3: Validate and Revise Skeleton
        validated_skeleton = await self.revise(
            instruction="""Critically review the mathematical skeleton:
            - Check unit consistency (e.g., can't add hours to dollars)
            - Ensure operations follow logical order (e.g., multiplication before addition if per-unit)
            - Flag any remaining ambiguities
            - Add constraints: no negative quantities for physical items, no fractional people
            - If algebra needed (e.g., 'half of total'), introduce 'x' and solve equation
            Revise the skeleton to fix all issues. If unfixable, output 'REDECOMPOSE'.""",
            context=skeleton
        )

        if "REDECOMPOSE" in validated_skeleton:
            # Redecompose with constraints
            decomposition = await self.decompose(
                instruction="""Redecompose with strict constraints:
                - All quantities must be non-negative
                - Discrete items (people, cookies) must be integers
                - If ambiguous, default to smallest plausible integer (e.g., 'কয়েকটি' → 3)
                Output revised frames.""",
                context=""
            )
            skeleton = await self.generate(
                instruction=f"""Regenerate skeleton with constraints:
                Decomposition: {decomposition}
                Follow same rules as before, but enforce non-negativity and integer constraints.""",
                context=decomposition
            )
            validated_skeleton = skeleton  # Skip re-validation for brevity

        # Step 4: Check for Ambiguity → Ensemble if needed
        if "AMBIGUOUS" in validated_skeleton or "plausible interpretations" in validated_skeleton:
            # Generate 3 interpretations
            interpretations = await asyncio.gather(
                self.generate(instruction=f"Interpretation 1: Replace ambiguous terms with minimal values (e.g., 'কয়েকটি'=3). Skeleton: {validated_skeleton}", context=""),
                self.generate(instruction=f"Interpretation 2: Replace ambiguous terms with moderate values (e.g., 'কয়েকটি'=5). Skeleton: {validated_skeleton}", context=""),
                self.generate(instruction=f"Interpretation 3: Replace ambiguous terms with maximal plausible values (e.g., 'কয়েকটি'=7). Skeleton: {validated_skeleton}", context="")
            )
            
            # Solve each interpretation
            solutions = await asyncio.gather(
                *[self.programmer(
                    instruction=f"""Generate and execute Python code for this interpretation:
                    - Use descriptive variables
                    - Enforce non-negative and integer constraints for discrete items
                    - Output ONLY the final numerical answer (no text, no units)
                    - If error, output 'ERROR'""",
                    context=interp
                ) for interp in interpretations]
            )
            
            # Ensemble: Select most plausible (integer, positive, smallest if tie)
            final_answer = await self.ensemble(
                instruction="""Select the best answer from the candidates:
                - Prefer integer over float (unless problem implies decimal)
                - Prefer positive over negative
                - Prefer smaller numbers (grade-school context)
                - If all invalid, select first non-ERROR
                Output ONLY the selected numerical value.""",
                contexts_list=solutions
            )
        else:
            # No ambiguity → Direct execution
            execution_result = await self.programmer(
                instruction=f"""Generate and execute Python code:
                Skeleton: {validated_skeleton}
                - Use descriptive variables
                - Enforce non-negative and integer constraints for discrete items
                - Output ONLY the final numerical answer (no text, no units)
                - If error, output 'RETRY'""",
                context=validated_skeleton
            )
            
            # Step 5: Sanity Check Loop (max 2 retries)
            for _ in range(2):
                if "RETRY" in execution_result or "ERROR" in execution_result:
                    validated_skeleton = await self.revise(
                        instruction=f"""Previous execution failed. Revise skeleton:
                        - Double-check operation order
                        - Ensure all variables are defined
                        - Add explicit type conversions if needed
                        - Simplify complex expressions
                        Output revised skeleton.""",
                        context=validated_skeleton
                    )
                    execution_result = await self.programmer(
                        instruction=f"""Retry with revised skeleton:
                        - Output ONLY final number
                        - If still error, output 'GIVE_UP'""",
                        context=validated_skeleton
                    )
                else:
                    break
            
            final_answer = execution_result

        # Step 6: Final Extraction and Cleanup
        answer = await self.summarize(
            instruction="""Extract the final numerical answer from the result. 
            - Remove any units, text, or explanations
            - If multiple numbers, select the last computed one
            - Ensure it's a valid number (integer or decimal)
            Output ONLY the number.""",
            context=final_answer
        )

        # Clean up answer (remove any residual text)
        match = re.search(r'[-+]?\d*\.?\d+', answer)
        if match:
            return match.group(0)
        else:
            return "0"  # Fallback