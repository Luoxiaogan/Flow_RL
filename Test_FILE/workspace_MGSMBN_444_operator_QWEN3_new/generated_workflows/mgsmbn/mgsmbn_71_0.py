# Workflow ID: mgsmbn_71_0
# Benchmark: mgsmbn
# Data Indices: [38]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for MGSM Bengali math word problems.
        Uses multi-perspective decomposition, cross-validation, iterative refinement, 
        and consensus synthesis to ensure robust, accurate numerical answers.
        """
        import asyncio

        # === PHASE 1: PARALLEL MULTI-PERSPECTIVE DECOMPOSITION ===
        # Generate 3 independent analyses from different reasoning lenses
        decomposition_instructions = [
            """
            You are a mathematical analyst. Your task is to extract ONLY the mathematical structure of the problem.
            - Identify all numbers and what they represent.
            - Determine the sequence of arithmetic operations needed.
            - Ignore narrative context; focus purely on quantities and relationships.
            - Show your step-by-step calculation plan.
            - Do NOT solve yet — only decompose.
            """,
            """
            You are a narrative analyst. Your task is to extract the story structure.
            - Who are the entities involved?
            - What actions occur, and in what order?
            - What is the explicit question being asked?
            - Map the chronological or causal flow of events.
            - Do NOT perform calculations — only describe the narrative logic.
            """,
            """
            You are a constraint analyst. Your task is to identify all physical, logical, or contextual constraints.
            - Are there unit requirements? (e.g., must be integer, non-negative, etc.)
            - Are there implicit real-world limits? (e.g., can't have negative people)
            - Does the context imply rounding or exactness?
            - Flag any potential inconsistencies or ambiguities.
            - Do NOT solve — only list constraints and boundary conditions.
            """
        ]

        # Generate all three in parallel
        decompositions = await asyncio.gather(
            self.generate(instruction=decomposition_instructions[0], context=""),
            self.generate(instruction=decomposition_instructions[1], context=""),
            self.generate(instruction=decomposition_instructions[2], context="")
        )

        # === PHASE 2: CROSS-REVISION & ITERATIVE VALIDATION ===
        revised_decompositions = []
        max_iterations = 2

        for i in range(len(decompositions)):
            current = decompositions[i]
            others = [decompositions[j] for j in range(len(decompositions)) if j != i]
            context_others = "\n\n".join(others)

            for iteration in range(max_iterations):
                # Revise each decomposition using insights from the other two
                revise_instruction = f"""
                You are refining your previous analysis. Consider the following perspectives from other analysts:

                {context_others}

                Now, revise your analysis to:
                - Correct any inconsistencies with the other views.
                - Fill in missing steps or constraints.
                - Ensure your logic aligns with both narrative flow and mathematical rigor.
                - If you find an error, explain and fix it.

                Maintain your original analytical lens (mathematical/narrative/constraint).
                """
                revised = await self.revise(instruction=revise_instruction, context=current)
                
                # Validate for fatal flaws (optional: could add regex or keyword check here)
                # For now, we assume revision improves quality
                current = revised

            revised_decompositions.append(current)

        # === PHASE 3: ENSEMBLE SYNTHESIS ===
        synthesis_instruction = """
        You are an expert elementary math teacher synthesizing three analytical perspectives into one correct answer.
        Guidelines:
        1. Prioritize solutions that respect unit consistency (e.g., no fractional people if context implies whole persons).
        2. Follow chronological or causal order described in the narrative.
        3. Prefer exact arithmetic over estimation unless specified.
        4. The final answer must directly respond to the problem's explicit question.
        5. If perspectives conflict, choose the one most grounded in both math and context.

        Output ONLY the final numerical answer (integer or decimal). Do not include units, explanations, or text.
        Example outputs: "42", "15.5", "0"
        """

        synthesized_answer = await self.ensemble(
            instruction=synthesis_instruction,
            contexts_list=revised_decompositions
        )

        # === PHASE 4: FINAL POLISH (EXTRACT PURE NUMERICAL ANSWER) ===
        extract_instruction = """
        Extract ONLY the final numerical value from the text below.
        - Remove any units (e.g., 'টাকা', 'জন', 'টি').
        - Remove any explanatory text, punctuation, or formatting.
        - If multiple numbers exist, choose the one that answers the problem's main question.
        - Output must be a clean number string: e.g., "30", "15.75", "0"
        - If no number is found, output "0" as fallback.
        """
        final_answer = await self.revise(
            instruction=extract_instruction,
            context=synthesized_answer
        )

        return final_answer.strip()