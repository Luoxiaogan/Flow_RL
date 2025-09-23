# Workflow ID: mgsmbn_107_0
# Benchmark: mgsmbn
# Data Indices: [75]

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

        # STEP 1: Decompose the problem into structured subproblems
        decomposition = await self.decompose(
            instruction="""Thoroughly decompose this Bengali math word problem into atomic, solvable subproblems. For each subproblem:
            - Identify the key entities (people, objects, quantities)
            - Extract all numerical values and their contextual meaning
            - Determine the mathematical relationship or operation required
            - Establish dependencies (which subproblems must be solved first)
            - Flag any unit conversions, hidden assumptions, or real-world constraints
            - Sequence steps chronologically or logically
            Return as a list of subproblem dictionaries with 'id', 'description', and 'dependencies'.""",
            context=""
        )

        # STEP 2: Parallel solution generation — semantic vs computational tracks
        semantic_plan_task = self.generate(
            instruction="""Based on the problem decomposition, construct a detailed natural language solution plan:
            - Restate each subproblem in clear, step-by-step form
            - Show intermediate calculations with explicit values
            - Track units throughout (e.g., ঘণ্টা, টাকা)
            - Highlight any proportional reasoning, fractions, or comparisons
            - Conclude with the final answer embedded in context
            - Ensure the plan answers exactly what was asked in the original question""",
            context=str(decomposition)
        )

        direct_code_task = self.programmer(
            instruction="""Generate Python code to solve the original Bengali math problem directly.
            - Parse and extract all numbers and relationships from the text
            - Implement necessary arithmetic, fractions, or comparisons
            - Include unit tracking in comments
            - Output only the final numerical answer (int or float)
            - Handle edge cases (e.g., division, negative results) with assertions
            - If ambiguous, choose the most contextually reasonable interpretation""",
            context="",
            max_retries=3
        )

        semantic_plan, direct_code_result = await asyncio.gather(semantic_plan_task, direct_code_task)

        # STEP 3: Refine both tracks
        refined_semantic = await self.revise(
            instruction="""Critically revise this solution plan:
            - Verify all intermediate calculations are mathematically correct
            - Ensure units are consistent and carried through each step
            - Confirm the final answer matches the question's request (e.g., difference, total, ratio)
            - Check for real-world plausibility (e.g., no negative sleep hours)
            - Explicitly state the final numerical answer at the end in the format: "ANSWER: X"
            - If any step is ambiguous or incorrect, correct it with reasoning""",
            context=semantic_plan
        )

        # Re-execute code if needed (auto-retry handled internally), but extract final answer
        # Programmer returns execution result; we need to parse the final number
        final_code_answer = None
        try:
            # Extract numerical answer from code output
            match = re.search(r"(?:answer|result|output)[:\s]*([+-]?\d*\.?\d+)", direct_code_result, re.IGNORECASE)
            if match:
                final_code_answer = match.group(1)
            else:
                # Fallback: take last number in output
                numbers = re.findall(r"[+-]?\d*\.?\d+", direct_code_result)
                if numbers:
                    final_code_answer = numbers[-1]
        except Exception:
            final_code_answer = "COMPUTATION_FAILED"

        # STEP 4: Ensemble — synthesize and validate
        ensemble_result = await self.ensemble(
            instruction=f"""You are given two solution attempts for a Bengali elementary math problem:
            1. SEMANTIC SOLUTION (natural language with reasoning):
            {refined_semantic}

            2. COMPUTATIONAL SOLUTION (code output):
            {direct_code_result}
            Extracted answer: {final_code_answer}

            Your task:
            - Compare the final numerical answers from both solutions
            - If they agree, select that answer
            - If they disagree, analyze which is more plausible:
                * Check unit consistency
                * Validate against real-world constraints (e.g., positivity, reasonableness)
                * Prefer computational precision unless semantic context overrides it
            - If both are flawed, synthesize a corrected answer using the best parts of each
            - Output ONLY the final numerical value (integer or decimal) — nothing else""",
            contexts_list=[refined_semantic, direct_code_result]
        )

        # STEP 5: Final sanity check — ensure answer matches question intent
        final_answer = await self.revise(
            instruction=f"""Perform a final validation of this answer: {ensemble_result}
            - Re-read the original Bengali question
            - Confirm this answer directly responds to what was asked (e.g., difference, total, remaining)
            - Ensure it’s in the correct units (implied by context)
            - Verify it’s reasonable (e.g., not greater than total quantities mentioned)
            - If correct, output the number unchanged
            - If flawed, recompute using the most reliable method (prioritize programmer output if available)
            - RETURN ONLY THE FINAL NUMERICAL VALUE — no text, no units, no explanation""",
            context=ensemble_result
        )

        # Extract clean numerical answer
        try:
            # Remove any non-numeric characters except decimal point and minus
            clean_answer = re.sub(r'[^\d\.\-]', '', final_answer.strip())
            float_val = float(clean_answer)
            # Return as int if whole number, else float
            return int(float_val) if float_val.is_integer() else float_val
        except Exception:
            # Fallback: return ensemble result as string if parsing fails
            return final_answer.strip()