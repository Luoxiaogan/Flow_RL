# Workflow ID: mgsmbn_76_0
# Benchmark: mgsmbn
# Data Indices: [164, 9]

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

        # Stage 1: Semantic Decomposition
        decomposition = await self.generate(
            instruction="""Thoroughly decompose the Bengali word problem into its core mathematical components. Extract:
            1. All named entities (people, objects) and their initial quantities.
            2. All actions (buy, sell, give, divide) with their numerical parameters and sequence.
            3. All units (টাকা, ঘণ্টা, জিনিস, ব্যাগ) and ensure consistency.
            4. The explicit question being asked (usually ends with 'কতগুলি?' or 'কতটি?').
            5. Any fractions, percentages, or ratios mentioned.
            6. Temporal or conditional constraints (e.g., 'তারপর', 'অবশিষ্ট', 'অর্ধেক').
            Format as a structured list with clear labels. Do not solve yet — only extract.""",
            context=""
        )

        # Stage 2: Parallel Reasoning Tracks
        linguistic_analysis, mathematical_modeling, validation_checks = await asyncio.gather(
            self.generate(
                instruction=f"""Analyze the Bengali text linguistically:
                - Resolve any ambiguous pronouns or references (e.g., 'সে', 'তার').
                - Clarify implied operations (e.g., 'অবশিষ্ট' implies subtraction, 'অর্ধেক' implies division by 2).
                - Identify any cultural or contextual assumptions (e.g., 'ব্যাগ' containing fixed quantities).
                - Flag any potentially misleading phrasing.
                Base your analysis strictly on this decomposition:
                {decomposition}
                Output a clear interpretation in simple Bengali-to-English mapping.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Build a precise mathematical model:
                - Translate all extracted quantities and actions into equations or step-by-step arithmetic.
                - Handle fractions, percentages, and reverse calculations explicitly.
                - Show intermediate variables (e.g., 'Let x be initial quantity').
                - Maintain unit tracking throughout.
                - If reverse calculation is needed (e.g., from remainder to initial), show algebraic steps.
                Use this decomposition as your foundation:
                {decomposition}
                Output the complete mathematical workflow with numbered steps.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate validation constraints:
                - List all physical/logical constraints (e.g., no negative people, integer counts).
                - Identify unit consistency requirements.
                - Predict plausible answer range (e.g., 'should be between 50-150 based on inputs').
                - Flag any potential calculation pitfalls (e.g., 'division before subtraction').
                Based on:
                {decomposition}
                Output as bullet points with justifications.""",
                context=decomposition
            )
        )

        # Stage 3: Ensemble Synthesis
        synthesized_approach = await self.ensemble(
            instruction="""Synthesize the three analyses into one coherent solution strategy:
            - Prioritize mathematical rigor but incorporate linguistic clarifications.
            - Enforce validation constraints (e.g., integer outputs, unit consistency).
            - Resolve conflicts by favoring explicit numerical relationships over narrative.
            - Output a step-by-step plan that combines the best of all three tracks.
            - Ensure the plan answers the exact question asked in the problem.""",
            contexts_list=[linguistic_analysis, mathematical_modeling, validation_checks]
        )

        # Stage 4: Iterative Refinement with Validation
        current_solution = synthesized_approach
        for iteration in range(3):
            validation_feedback = await self.generate(
                instruction=f"""Critically validate this solution:
                - Check arithmetic accuracy step by step.
                - Verify unit consistency and conversion.
                - Ensure answer satisfies all constraints (non-negative, integer if required).
                - Confirm it answers the original question.
                - Flag any logical gaps or assumptions.
                If no issues, output 'VALID'. Otherwise, list specific errors.
                Solution to validate:
                {current_solution}""",
                context=current_solution
            )

            if "VALID" in validation_feedback.upper() and "ERROR" not in validation_feedback.upper():
                break

            current_solution = await self.revise(
                instruction=f"""Revise the solution based on this feedback:
                {validation_feedback}
                - Fix all identified errors.
                - Maintain step-by-step clarity.
                - Re-verify unit handling and constraints.
                - If fractional result where integer expected, adjust logic (e.g., floor/ceiling if context allows).
                Original solution:
                {current_solution}""",
                context=current_solution
            )

        # Stage 5: Final Answer Extraction
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the solution.
            - It must be a single number (integer or decimal).
            - Ignore units, explanations, or intermediate values.
            - If multiple numbers exist, select the one that directly answers 'কতগুলি?' or 'কতটি?'.
            - Double-check against the original question's requirement.
            Solution:
            """ + current_solution,
            context=current_solution
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer)
        return cleaned if cleaned else "0"