# Workflow ID: mgsmbn_119_0
# Benchmark: mgsmbn
# Data Indices: [44]

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

        # === PHASE 1: SEMANTIC DECONSTRUCTION ===
        problem_analysis = await self.generate(
            instruction="""Perform deep semantic analysis of this Bengali math word problem. Extract and structure:

1. ENTITIES: List all objects, people, containers (e.g., 'ঝুড়ি', 'কমলালেবু', 'রহিম'). For each, note quantity if mentioned.
2. NUMERICAL VALUES: Extract every number and its semantic role. Is it a total? A percentage? A rate? A remainder?
3. OPERATIONS: What mathematical operations are implied? (addition, subtraction, percentage of, ratio, etc.)
4. CONSTRAINTS: What real-world or logical constraints apply? (e.g., 'must be integer', 'cannot exceed total', 'percentage base')
5. UNKNOWN: What is the question asking for? Rephrase it mathematically.

Format output as a structured markdown list with clear section headers. Be exhaustive.""",
            context=""
        )

        # === PHASE 2: PARALLEL SOLUTION PATHS ===
        # Three independent reasoning strategies
        direct_path, constraint_path, narrative_path = await asyncio.gather(
            self.generate(
                instruction=f"""SOLVE DIRECTLY using extracted values:
- Use the numbers and operations from analysis: {problem_analysis}
- Perform calculations step by step
- Show intermediate results
- Output final answer as: "ANSWER: X" where X is the number
- Do NOT overthink — assume straightforward interpretation""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""SOLVE WITH CONSTRAINTS:
- Use analysis: {problem_analysis}
- Explicitly model ALL constraints (integer values, percentage bases, unit consistency)
- Set up equations if needed
- Solve algebraically
- Verify answer satisfies ALL constraints
- Output: "ANSWER: X" with verification notes""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""SOLVE VIA NARRATIVE RECONSTRUCTION:
- Re-tell the problem as a chronological story
- At each story step, write the corresponding mathematical operation
- Track running totals/quantities
- Derive answer from final story state
- Output: "ANSWER: X" with story summary""",
                context=problem_analysis
            )
        )

        # === PHASE 3: ADVERSARIAL CRITIQUE ===
        # Each solution critiques itself
        direct_critique, constraint_critique, narrative_critique = await asyncio.gather(
            self.revise(
                instruction="""CRITIQUE THIS SOLUTION ADVERSARIALLY:
- Assume this solution is WRONG. Where is the most likely error?
- Check: unit consistency, integer constraints, operation order, percentage base, total sum
- Is the answer plausible? Does it violate real-world constraints?
- If no error found, state "NO OBVIOUS ERROR"
- Be specific and technical""",
                context=direct_path
            ),
            self.revise(
                instruction="""CRITIQUE THIS SOLUTION ADVERSARIALLY:
- Assume this solution is WRONG. Where is the most likely error?
- Check: unit consistency, integer constraints, operation order, percentage base, total sum
- Is the answer plausible? Does it violate real-world constraints?
- If no error found, state "NO OBVIOUS ERROR"
- Be specific and technical""",
                context=constraint_path
            ),
            self.revise(
                instruction="""CRITIQUE THIS SOLUTION ADVERSARIALLY:
- Assume this solution is WRONG. Where is the most likely error?
- Check: unit consistency, integer constraints, operation order, percentage base, total sum
- Is the answer plausible? Does it violate real-world constraints?
- If no error found, state "NO OBVIOUS ERROR"
- Be specific and technical""",
                context=narrative_path
            )
        )

        # === PHASE 4: META-ENSEMBLE WITH ERROR-AWARE SELECTION ===
        final_answer = await self.ensemble(
            instruction="""SELECT OR SYNTHESIZE BEST ANSWER:
You have three solutions with their critiques:
1. Direct: {direct_path} | Critique: {direct_critique}
2. Constraint: {constraint_path} | Critique: {constraint_critique}
3. Narrative: {narrative_path} | Critique: {narrative_critique}

STRATEGY:
- If one solution's critique is clearly less severe (e.g., "NO OBVIOUS ERROR" vs "violates integer constraint"), choose that.
- If critiques reveal complementary insights, SYNTHESIZE a new answer.
- If all have fatal flaws, pick the least wrong and flag uncertainty.
- OUTPUT ONLY THE NUMERICAL ANSWER as: "ANSWER: X"

DO NOT explain — just output the number in the required format.""".format(
                direct_path=direct_path,
                direct_critique=direct_critique,
                constraint_path=constraint_path,
                constraint_critique=constraint_critique,
                narrative_path=narrative_path,
                narrative_critique=narrative_critique
            ),
            contexts_list=[direct_path, constraint_path, narrative_path]
        )

        # === PHASE 5: SANITY CHECK & AUTO-CORRECT ===
        sanity_check = await self.generate(
            instruction=f"""VALIDATE FINAL ANSWER:
Problem: {self.problem_text}
Proposed Answer: {final_answer}

Check:
1. Does this answer make sense in context? (e.g., if total items=25, answer cannot be 30)
2. Do all intermediate steps add up? (show quick verification math)
3. Are units consistent?
4. Is it an integer if required?

If VALID: output "VALID: X"
If INVALID: output "INVALID: correct answer should be Y"

OUTPUT ONLY in this format.""".replace("{final_answer}", final_answer),
            context=final_answer
        )

        # Extract number from sanity check if valid, else trigger fallback
        if "VALID:" in sanity_check:
            final_number = re.search(r"VALID:\s*([0-9\.]+)", sanity_check)
            if final_number:
                return final_number.group(1)
        
        # Fallback: return original ensemble answer (sanity check may have formatting issues)
        final_number = re.search(r"ANSWER:\s*([0-9\.]+)", final_answer)
        if final_number:
            return final_number.group(1)
        
        # Last resort: extract any number from ensemble output
        fallback_number = re.search(r"([0-9]+\.?[0-9]*)", final_answer)
        if fallback_number:
            return fallback_number.group(1)
        
        # Ultimate fallback
        return "0"