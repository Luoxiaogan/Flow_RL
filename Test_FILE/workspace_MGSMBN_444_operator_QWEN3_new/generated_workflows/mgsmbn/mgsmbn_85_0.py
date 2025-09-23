# Workflow ID: mgsmbn_85_0
# Benchmark: mgsmbn
# Data Indices: [37, 189]

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

        # STEP 1: STRUCTURED EXTRACTION OF ENTITIES, UNITS, ACTIONS, AND GOAL
        extraction = await self.generate(
            instruction="""You are a mathematical linguist analyzing a Bengali word problem. Your task is to extract and structure ALL key components with absolute precision.

            Extract and categorize the following:
            - PEOPLE: List all named or implied actors (e.g., ট্রেসি, জন, বন্ধুরা) and their roles.
            - OBJECTS: Physical or abstract items involved (e.g., তার, পিৎজা, টুকরো).
            - QUANTITIES: All numerical values with their associated entities and units (e.g., "4 ফুট" → value=4, unit=ফুট, entity=তার).
            - ACTIONS: Verbs or operations described (e.g., কাটা, অর্ডার দিয়েছিলেন, পাবেন).
            - RELATIONSHIPS: How quantities relate (e.g., "প্রত্যেকে 4 টুকরো পাবে" → per-person allocation).
            - CONSTRAINTS: Explicit or implicit limitations (e.g., "কেবলমাত্র 8 টুকরো ভাগে পিৎজা বিক্রি হয়" → indivisible units).
            - GOAL: The explicit question being asked (e.g., "কতগুলি টুকরো পেয়েছিলেন?" → count of wire pieces).

            Format your output as a structured markdown list with clear section headers. Be exhaustive. Disambiguate units (e.g., ফুট vs. ইঞ্চি). Flag any term that could have multiple interpretations.""",
            context=""
        )

        # STEP 2: PARALLEL REASONING PATHWAYS (Mathematical, Linguistic, Constraint-Based)
        math_path, linguistic_path, constraint_path = await asyncio.gather(
            self.generate(
                instruction=f"""You are a mathematical modeler. Given the structured extraction below, derive a complete, step-by-step computational solution.

                STRUCTURED EXTRACTION:
                {extraction}

                Instructions:
                - Identify the sequence of arithmetic operations needed (add, subtract, multiply, divide, convert units, apply ceiling/floor).
                - Show intermediate calculations with units tracked at each step.
                - Justify why each operation is applied (e.g., "multiply because total = per-unit × count").
                - If unit conversion is needed (e.g., feet to inches), show the conversion factor explicitly.
                - If the problem implies a constraint (e.g., must round up), state it and apply it.
                - Output the final numerical answer at the end, but also show the full derivation.

                Do NOT skip steps. Do NOT assume prior knowledge. Treat this as a proof.""",
                context=extraction
            ),
            self.generate(
                instruction=f"""You are a Bengali linguistic analyst. Re-examine the original problem and the extraction below. Your goal is to validate semantic intent and flag ambiguities.

                STRUCTURED EXTRACTION:
                {extraction}

                Instructions:
                - Re-read the original Bengali text. Does the extraction accurately capture all nuances?
                - Are there phrases that imply mathematical operations not explicitly stated? (e.g., "নিশ্চিত করতে চান" → implies ≥ constraint → ceiling).
                - Are units or quantities misinterpreted? (e.g., "টুকরো" as pieces vs. fragments).
                - Does the goal question have only one possible interpretation?
                - Highlight any term or phrase whose mathematical mapping is ambiguous or context-dependent.

                Output a list of potential linguistic pitfalls or misinterpretations that could derail the mathematical solution.""",
                context=extraction
            ),
            self.generate(
                instruction=f"""You are a constraint and unit auditor. Validate physical and mathematical consistency.

                STRUCTURED EXTRACTION:
                {extraction}

                Instructions:
                - Verify that all operations respect unit consistency (e.g., can't add feet to inches without conversion).
                - Flag any step that would produce a physically impossible result (e.g., fractional people, negative quantities).
                - Ensure the final answer type matches the problem's requirement (integer for countable items, decimal for measurements).
                - Check if implicit constraints (e.g., indivisible units, minimum allocations) are respected.
                - If unit conversion is needed, verify the conversion factor is correct (e.g., 1 foot = 12 inches).

                Output a list of constraint violations or unit mismatches that must be corrected.""",
                context=extraction
            )
        )

        # STEP 3: SYNTHESIZE PATHWAYS INTO COHERENT SOLUTION
        synthesized_solution = await self.ensemble(
            instruction="""You are a master problem-solver synthesizing three expert perspectives: mathematical, linguistic, and constraint-based. Your task is to produce a single, flawless, step-by-step solution.

            Guidelines:
            - Prioritize linguistic intent over mathematical convenience. If the language implies a constraint (e.g., "must ensure"), enforce it even if mathematically inconvenient.
            - Prioritize constraint validity over both. No fractional people, no negative quantities, no unit mismatches.
            - Resolve conflicts by cross-referencing all three inputs. If math says 7.5 pizzas but constraint says indivisible units and linguistic says "ensure everyone gets 4", then round up to 8.
            - Show the full derivation with units and justifications.
            - End with the final numerical answer on its own line, prefixed by "FINAL ANSWER: ".

            Output only the synthesized solution. No meta-commentary.""",
            contexts_list=[math_path, linguistic_path, constraint_path]
        )

        # STEP 4: VALIDATION LOOP (up to 3 iterations)
        current_solution = synthesized_solution
        for _ in range(3):
            validation = await self.revise(
                instruction="""You are a skeptical elementary school teacher grading this solution. Critique it ruthlessly.

                Check:
                1. Does each step follow logically from the previous? No leaps.
                2. Are units handled correctly at every step? Show conversions explicitly.
                3. Is the final answer an integer or decimal as required by the problem's context?
                4. Does it respect real-world constraints? (e.g., can't order half a pizza if sold whole).
                5. Are there any hidden steps or assumptions not justified?

                If you find ANY issue, revise the solution to fix it. Clearly state what you changed and why.
                If no issues, output "VALID: " followed by the unchanged solution.""",
                context=current_solution
            )
            
            if "VALID:" in validation:
                current_solution = validation.replace("VALID: ", "").strip()
                break
            else:
                current_solution = validation  # Use revised version for next iteration

        # STEP 5: EXTRACT PURE NUMERICAL ANSWER
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the solution below. 

            Rules:
            - It must be a single number (integer or decimal).
            - Remove all units, labels, explanations, and punctuation.
            - If multiple numbers appear, select the one that directly answers the problem's explicit question.
            - If the solution ends with "FINAL ANSWER: X", extract X.
            - Output nothing else — just the number.

            Example valid outputs: "8", "10.5", "0", "100".""",
            context=current_solution
        )

        # Clean and return final answer
        # Remove any accidental text, keep only digits and decimal point
        cleaned = re.sub(r'[^\d\.]', '', final_answer.strip())
        return cleaned