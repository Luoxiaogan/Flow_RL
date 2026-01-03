# Workflow ID: mgsmbn_37_0
# Benchmark: mgsmbn
# Data Indices: [113]

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

        # STEP 1: Generate a structured problem schema (entities, events, constraints, goal)
        schema = await self.generate(
            instruction="""Thoroughly decompose the Bengali word problem into a structured schema. Identify:
            1. All entities (people, objects, exams, etc.) and their initial states.
            2. All events or actions (what happens, when, and to whom).
            3. All numerical values, their units, and what they represent.
            4. The explicit question being asked and the unknown to solve for.
            5. Any implicit constraints (e.g., non-negative quantities, real-world limits).
            Format the output as a clear, labeled breakdown with sections: ENTITIES, EVENTS, VALUES, GOAL, CONSTRAINTS.""",
            context=""
        )

        # STEP 2: Parallel generation of three distinct solution strategies
        chronological, algebraic, proportional = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using a CHRONOLOGICAL approach:
                - Reconstruct the timeline of events exactly as described.
                - Track state changes step by step (e.g., questions attempted per hour, cumulative totals).
                - Calculate intermediate values explicitly.
                - Ensure units are tracked at every step (e.g., প্রশ্ন, ঘণ্টা).
                - Verify that the final answer matches the problem's goal.
                Base your reasoning on this schema:
                {schema}""",
                context=schema
            ),
            self.generate(
                instruction=f"""Solve the problem using an ALGEBRAIC approach:
                - Define variables for unknown quantities.
                - Translate relationships into equations (e.g., rate × time = quantity).
                - Solve equations step by step, showing substitutions and simplifications.
                - Check that the solution satisfies all constraints from the schema.
                - Express the final answer numerically.
                Base your reasoning on this schema:
                {schema}""",
                context=schema
            ),
            self.generate(
                instruction=f"""Solve the problem using a PROPORTIONAL approach:
                - Identify rates, ratios, or scaling factors (e.g., questions per hour).
                - Use proportional reasoning to extrapolate or compare (e.g., if 75 questions take 8 hours, how many in 6?).
                - Handle unit conversions explicitly.
                - Cross-validate with total quantities mentioned.
                - Ensure the answer is contextually sensible (e.g., no fractional questions if inappropriate).
                Base your reasoning on this schema:
                {schema}""",
                context=schema
            )
        )

        # STEP 3: Revise each solution for mathematical and logical soundness
        revised_chrono, revised_algebra, revised_prop = await asyncio.gather(
            self.revise(
                instruction="""Critically revise this solution:
                - Verify every arithmetic operation for accuracy.
                - Ensure units are consistent and properly carried through (e.g., প্রশ্ন/ঘণ্টা × ঘণ্টা = প্রশ্ন).
                - Check that the answer satisfies the original problem's constraints (e.g., non-negative, integer if required).
                - Flag any assumptions not grounded in the problem text.
                - Improve clarity and step-by-step justification.""",
                context=chronological
            ),
            self.revise(
                instruction="""Critically revise this solution:
                - Verify every arithmetic operation for accuracy.
                - Ensure units are consistent and properly carried through (e.g., প্রশ্ন/ঘণ্টা × ঘণ্টা = প্রশ্ন).
                - Check that the answer satisfies the original problem's constraints (e.g., non-negative, integer if required).
                - Flag any assumptions not grounded in the problem text.
                - Improve clarity and step-by-step justification.""",
                context=algebraic
            ),
            self.revise(
                instruction="""Critically revise this solution:
                - Verify every arithmetic operation for accuracy.
                - Ensure units are consistent and properly carried through (e.g., প্রশ্ন/ঘণ্টা × ঘণ্টা = প্রশ্ন).
                - Check that the answer satisfies the original problem's constraints (e.g., non-negative, integer if required).
                - Flag any assumptions not grounded in the problem text.
                - Improve clarity and step-by-step justification.""",
                context=proportional
            )
        )

        # STEP 4: Ensemble synthesis — merge the three revised solutions into one authoritative answer
        synthesized = await self.ensemble(
            instruction="""Synthesize the three revised solutions into a single, definitive answer:
            - Identify points of consensus (e.g., all agree total attempted = 175).
            - Resolve discrepancies by cross-referencing with the original problem schema.
            - Prioritize solutions that explicitly track units and show step-by-step work.
            - If one solution is clearly more complete or accurate, adopt its reasoning.
            - Extract the final numerical answer and ensure it is a standalone number (integer or decimal).
            - Do NOT include units or explanations in the final output — only the number.""",
            contexts_list=[revised_chrono, revised_algebra, revised_prop]
        )

        # STEP 5: Fallback loop — if synthesis shows uncertainty, re-analyze and retry
        if any(phrase in synthesized.lower() for phrase in ["assume", "possibly", "if", "unclear", "conflict"]):
            failure_analysis = await self.generate(
                instruction=f"""Diagnose why the first synthesis was uncertain:
                - What part of the problem was misinterpreted?
                - Which constraint or value was overlooked?
                - What assumption led to divergence?
                Based on this, regenerate a corrected problem schema and solution.""",
                context=f"Original Schema: {schema}\nSynthesized Output: {synthesized}"
            )
            
            # Regenerate one final solution using the corrected analysis
            final_attempt = await self.generate(
                instruction=f"""Using the corrected analysis, produce one final solution:
                - Be explicit, step-by-step, and unit-aware.
                - Derive the answer with no ambiguity.
                - Output ONLY the numerical answer at the end.""",
                context=failure_analysis
            )
            synthesized = final_attempt

        # STEP 6: Summarize to extract pure numerical answer
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the text below.
            - Remove all units, explanations, and reasoning.
            - If multiple numbers exist, select the one that answers the original question.
            - Return ONLY the number (integer or decimal), nothing else.""",
            context=synthesized
        )

        # Clean and return the answer
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer.strip())
        return cleaned