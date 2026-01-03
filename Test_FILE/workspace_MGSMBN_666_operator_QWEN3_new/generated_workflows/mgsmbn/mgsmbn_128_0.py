# Workflow ID: mgsmbn_128_0
# Benchmark: mgsmbn
# Data Indices: [92, 134]

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

        # Step 1: Semantic Decomposition - Extract entities, quantities, relationships, and unknowns
        decomposition_context = await self.generate(
            instruction="""You are a Bengali mathematics expert. Analyze the word problem and extract:
            1. All numerical values with their units and contextual meaning (e.g., "7:13" is a ratio of sugar to water)
            2. The unknown quantity being asked for
            3. Key relationships (ratios, sequences, comparisons, distributions)
            4. Implicit constraints (non-negative, integer-only, unit consistency)
            5. Chronological or logical dependencies between events
            Format your output as a structured JSON with keys: "quantities", "unknown", "relationships", "constraints", "dependencies".""",
            context=""
        )

        # Step 2: Problem Classification - Determine problem type to guide solution strategy
        problem_type = await self.generate(
            instruction=f"""Based on the decomposition:
            {decomposition_context}
            
            Classify this problem into exactly one primary type:
            - "Proportional" (ratios, percentages, scaling)
            - "Sequential" (step-by-step operations, deposits/withdrawals)
            - "Rate" (speed/time, work rate, unit price)
            - "Distribution" (sharing, division with remainders)
            - "Comparison" (differences, "how many more")
            - "MultiEntity" (multiple actors with different quantities)
            
            Also assess confidence level (High/Medium/Low). If confidence is Low, recommend exploring multiple strategies.
            Output format: {{"type": "...", "confidence": "...", "notes": "..."}}""",
            context=decomposition_context
        )

        # Step 3: Conditional Strategy Branching
        try:
            type_info = json.loads(problem_type)
            problem_category = type_info.get("type", "Sequential")
            confidence = type_info.get("confidence", "High")
        except:
            problem_category = "Sequential"
            confidence = "Medium"

        # Step 4: Parallel Strategy Generation (if low confidence or complex type)
        if confidence == "Low" or problem_category in ["Proportional", "MultiEntity"]:
            strategy_contexts = await asyncio.gather(
                self.generate(
                    instruction=f"""Strategy 1: Algebraic Modeling
                    Convert the problem into algebraic equations. Define variables for unknowns. Solve symbolically.
                    Use the decomposition: {decomposition_context}
                    Show all steps and final equation.""",
                    context=decomposition_context
                ),
                self.generate(
                    instruction=f"""Strategy 2: Unit-Based Simulation
                    Simulate the problem step by step as if performing real-world actions. Track units and state changes.
                    Use the decomposition: {decomposition_context}
                    Show intermediate states and final result.""",
                    context=decomposition_context
                ),
                self.generate(
                    instruction=f"""Strategy 3: Ratio/Proportion Scaling
                    If applicable, normalize ratios or scale quantities proportionally. Use cross-multiplication or unitary method.
                    Use the decomposition: {decomposition_context}
                    Show scaling factors and final calculation.""",
                    context=decomposition_context
                )
            )
            
            # Synthesize best strategy via ensemble
            selected_strategy = await self.ensemble(
                instruction="""Evaluate the three strategies:
                1. Which is most mathematically sound?
                2. Which best preserves unit consistency?
                3. Which aligns with the problem's narrative structure?
                4. Which is least likely to have arithmetic errors?
                Select the single best approach and output it verbatim.""",
                contexts_list=strategy_contexts
            )
        else:
            # High confidence - use direct strategy
            selected_strategy = await self.generate(
                instruction=f"""Apply the {problem_category} strategy directly:
                {decomposition_context}
                Show clear, step-by-step reasoning with explicit calculations.
                Highlight the final numerical answer at the end.""",
                context=decomposition_context
            )

        # Step 5: Code-Grounded Calculation - Convert strategy to executable code
        code_result = await self.programmer(
            instruction=f"""Generate Python code that implements the following solution strategy:
            {selected_strategy}
            
            Requirements:
            - Use only basic arithmetic and math operations
            - Define variables with meaningful names
            - Include comments explaining each step
            - Print ONLY the final numerical answer (no text, no units)
            - Handle edge cases (division by zero, negative results where invalid)
            - Round to integer if context implies discrete quantities (people, items)""",
            context=selected_strategy,
            max_retries=3
        )

        # Step 6: Contextual Validation - Verify answer makes sense
        validation = await self.generate(
            instruction=f"""Validate the result: {code_result}
            Against original problem: {self.problem_text}
            And decomposition: {decomposition_context}
            
            Check:
            1. Does the number make sense in context? (e.g., no negative money, fractional people)
            2. Are units consistent? (if applicable)
            3. Does it satisfy all stated constraints?
            4. Is the magnitude reasonable? (order of magnitude check)
            
            If any issue, explain what's wrong. Otherwise, output "VALID".""",
            context=code_result
        )

        # Step 7: Revision Loop (if validation fails)
        final_result = code_result
        if "VALID" not in validation.upper():
            # Attempt revision
            revised_strategy = await self.revise(
                instruction=f"""The solution failed validation: {validation}
                Revise the strategy to fix the issue. Consider:
                - Unit conversion errors
                - Misinterpreted ratios
                - Incorrect operation order
                - Missing constraints
                Output revised step-by-step solution.""",
                context=selected_strategy
            )
            
            # Recalculate
            final_result = await self.programmer(
                instruction=f"""Implement revised solution:
                {revised_strategy}
                Print ONLY the final numerical answer.""",
                context=revised_strategy,
                max_retries=2
            )

        # Step 8: Final Answer Extraction - Ensure clean numerical output
        answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the following text.
            Remove all units, explanations, and text. If multiple numbers, pick the one that answers the original question.
            If no clear number, output 0.""",
            context=final_result
        )

        return answer.strip()