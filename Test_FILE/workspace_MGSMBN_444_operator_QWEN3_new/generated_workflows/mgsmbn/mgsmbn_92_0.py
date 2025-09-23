# Workflow ID: mgsmbn_92_0
# Benchmark: mgsmbn
# Data Indices: [95, 196]

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

        # STEP 1: PARALLEL SEMANTIC DECOMPOSITION — Generate three complementary perspectives
        perspectives = await asyncio.gather(
            self.generate(
                instruction="""You are an expert in mathematical word problem analysis. Extract and structure the problem from an ENTITY-CENTRIC perspective.
                Identify:
                - All named entities (people, objects, places)
                - Initial quantities associated with each entity
                - Actions performed by or on each entity
                - Final states or target unknowns
                Format as a structured narrative with clear subject-verb-object relationships.
                Example: 'Griffin starts with 24 fries. Kyle takes 5. Billy takes twice what Kyle took...'""",
                context=""
            ),
            self.generate(
                instruction="""You are an expert in mathematical word problem analysis. Extract and structure the problem from a TIME-CENTRIC perspective.
                Identify:
                - Chronological sequence of events
                - Temporal markers (before, after, then, finally)
                - State changes over time for each quantity
                - Dependencies between events
                Format as a timeline: 'At t=0: ... At t=1: ... Final state: ...'""",
                context=""
            ),
            self.generate(
                instruction="""You are an expert in mathematical word problem analysis. Extract and structure the problem from a MATH-RELATIONSHIP perspective.
                Identify:
                - All numerical values and their meanings
                - Mathematical operations implied (add, subtract, multiply, divide, percentage, ratio)
                - Unknown variables and what they represent
                - Equations or inequalities that must be satisfied
                Format as a system of mathematical statements with clear variable definitions.""",
                context=""
            )
        )

        # STEP 2: PARALLEL SOLUTION DRAFTING — Generate initial solution attempts from each perspective
        solution_drafts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Using the following problem decomposition:
                {perspective}
                
                Generate a complete step-by-step solution attempt. Show all calculations. Define variables clearly. 
                Do NOT skip steps. End with a boxed final answer. If multiple interpretations are possible, pick the most straightforward one.
                IMPORTANT: Track units and entity states throughout. Do not assume — derive from given information.""",
                context=perspective
            ) for perspective in perspectives]
        )

        # STEP 3: VALIDATION & REVISION — Critique each draft for logical consistency and constraint satisfaction
        revised_solutions = await asyncio.gather(
            *[self.revise(
                instruction="""Critically review this solution draft. Check for:
                1. Arithmetic errors in calculations
                2. Violation of real-world constraints (e.g., negative quantities, fractional people when inappropriate)
                3. Misinterpretation of temporal sequence
                4. Incorrect application of percentages or ratios
                5. Units mismatch or untracked units
                6. Logical gaps in reasoning
                
                If errors are found, correct them and explain the fix. If no errors, enhance clarity and add explicit verification steps.
                Preserve the step-by-step structure. End with the corrected boxed answer.""",
                context=draft
            ) for draft in solution_drafts]
        )

        # STEP 4: ENSEMBLE — Synthesize the best elements into a coherent, verified solution
        final_solution = await self.ensemble(
            instruction="""You are synthesizing multiple solution attempts for a mathematical word problem. Your goal is to produce the single most accurate, complete, and logically sound solution.
            
            Consider:
            - Which solution correctly models the sequence of events?
            - Which maintains consistent units and entity states?
            - Which handles edge cases and constraints appropriately?
            - Which provides the clearest step-by-step justification?
            
            If solutions conflict, identify the source of disagreement and resolve it by referring back to the original problem text.
            Synthesize a hybrid solution if necessary, combining the strongest elements from each draft.
            Present the final answer as a single numerical value in a box: \\boxed{{answer}}
            Include just enough steps to justify the answer — no more, no less.""",
            contexts_list=revised_solutions
        )

        # STEP 5: FINAL SUMMARIZATION — Condense into clean, minimal derivation ending with answer
        polished_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the solution below. 
            The answer must be a single number (integer or decimal) with no units or text.
            If the solution contains multiple numbers, select the one that directly answers the problem's main question.
            If no clear answer is present, return '0' as fallback.
            DO NOT include any reasoning, steps, or explanations — only the number.""",
            context=final_solution
        )

        return polished_answer.strip()