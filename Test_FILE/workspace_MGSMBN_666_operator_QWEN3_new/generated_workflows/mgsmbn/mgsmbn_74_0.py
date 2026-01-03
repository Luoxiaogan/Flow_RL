# Workflow ID: mgsmbn_74_0
# Benchmark: mgsmbn
# Data Indices: [18]

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

        # PHASE 1: PARALLEL DECOMPOSITION & MATHEMATICAL FRAMING
        decomposition_task = self.decompose(
            instruction="""Break this Bengali math problem into atomic subproblems.
            For each subproblem:
            - Identify what needs to be calculated or inferred
            - List required inputs and their sources
            - Specify dependencies on other subproblems
            - Flag any unit conversions or hidden assumptions
            - Identify if the subproblem involves: percentages, ratios, sequences, distributions, or comparisons
            Output as structured list of subproblems with clear IDs and dependency chains.""",
            context=""
        )

        framing_task = self.generate(
            instruction="""Analyze this Bengali word problem and generate a high-level mathematical framework.
            Specifically:
            - Identify the type of problem (percentage, rate, distribution, comparison, etc.)
            - Extract all numerical values and their semantic roles (e.g., 'discount rate', 'total quantity')
            - Infer the governing mathematical relationships (equations, proportions, inequalities)
            - State any implicit constraints (e.g., 'must be integer', 'non-negative', 'unit consistency')
            - Propose the general solution strategy (algebraic, sequential, proportional, etc.)
            Output as a structured analysis with clear sections.""",
            context=""
        )

        decomposition, framing = await asyncio.gather(decomposition_task, framing_task)

        # PHASE 2: SYMBOLIC FORMULATION
        symbolic_formulation = await self.generate(
            instruction=f"""Based on the decomposition and framing below, generate the precise symbolic formulation.
            Decomposition: {decomposition}
            Framing: {framing}
            
            Your task:
            - Write explicit equations or proportional relationships
            - Define all variables with units
            - Specify the target variable to solve for
            - Include any necessary unit conversions
            - Flag any assumptions made during formulation
            Output as a clean, mathematically rigorous specification ready for computation.""",
            context=f"{decomposition}\n\n{framing}"
        )

        # PHASE 3: PARALLEL SOLUTION ATTEMPTS
        # Path A: Programmer-based direct computation
        programmer_solution = await self.programmer(
            instruction=f"""Solve using the symbolic formulation below.
            Formulation: {symbolic_formulation}
            
            Requirements:
            - Generate precise Python code that computes the answer
            - Include unit tracking in comments
            - Validate intermediate steps
            - Return only the final numerical answer
            - Handle edge cases (division by zero, negative results) gracefully""",
            context=symbolic_formulation
        )

        # Path B: Step-by-step manual calculation
        manual_solution = await self.generate(
            instruction=f"""Solve step-by-step manually using the symbolic formulation below.
            Formulation: {symbolic_formulation}
            
            Requirements:
            - Show each calculation step explicitly
            - Justify each operation with reference to the problem context
            - Track units throughout
            - Verify intermediate results make sense
            - Box the final answer at the end
            Output as a detailed, human-readable solution narrative.""",
            context=symbolic_formulation
        )

        # PHASE 4: ENSEMBLE SYNTHESIS
        final_answer = await self.ensemble(
            instruction="""Compare the two solution paths below and synthesize the most reliable answer.
            - If both agree, return the answer
            - If they disagree, identify which is more plausible based on problem constraints
            - Check for unit consistency, sign, and real-world plausibility
            - If uncertainty remains, choose the answer that best satisfies implicit constraints
            - Output ONLY the final numerical answer, nothing else.
            
            CRITICAL: The answer must be a single number (integer or decimal) with no units or text.""",
            contexts_list=[programmer_solution, manual_solution]
        )

        # PHASE 5: META-VALIDATION (with fallback)
        for attempt in range(3):
            validation = await self.generate(
                instruction=f"""Validate the answer against the original problem.
                Answer: {final_answer}
                Problem: {self.problem_text}
                
                Check:
                - Is the answer positive? (unless context allows negative)
                - Is it integer when counting discrete items?
                - Does it match expected units?
                - Does it satisfy all constraints from framing?
                - Is it within plausible range?
                
                If valid, respond "VALID". If invalid, explain why concisely.""",
                context=final_answer
            )

            if "VALID" in validation.upper():
                break
            else:
                # Revisit symbolic formulation with validation feedback
                symbolic_formulation = await self.revise(
                    instruction=f"""Revise the symbolic formulation based on validation feedback.
                    Feedback: {validation}
                    Original Formulation: {symbolic_formulation}
                    
                    Adjust assumptions, constraints, or relationships as needed.
                    Focus on fixing the specific issue raised in feedback.""",
                    context=symbolic_formulation
                )

                # Recompute both paths
                programmer_solution = await self.programmer(
                    instruction=f"""Re-solve with revised formulation: {symbolic_formulation}""",
                    context=symbolic_formulation
                )

                manual_solution = await self.generate(
                    instruction=f"""Re-solve manually with revised formulation: {symbolic_formulation}""",
                    context=symbolic_formulation
                )

                final_answer = await self.ensemble(
                    instruction="""Re-synthesize answer from revised solutions. Output ONLY number.""",
                    contexts_list=[programmer_solution, manual_solution]
                )
        else:
            # Final fallback: take programmer solution as last resort
            final_answer = programmer_solution

        # Extract just the number (in case ensemble output has extra text)
        number_match = re.search(r'[-+]?\d*\.\d+|\d+', str(final_answer))
        if number_match:
            return number_match.group(0)
        else:
            return final_answer  # fallback if no number found