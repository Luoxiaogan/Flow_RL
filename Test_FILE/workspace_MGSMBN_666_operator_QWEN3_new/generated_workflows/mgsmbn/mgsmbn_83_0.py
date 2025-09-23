# Workflow ID: mgsmbn_83_0
# Benchmark: mgsmbn
# Data Indices: [46, 9]

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

        # PHASE 1: SEMANTIC DECOMPOSITION & PROBLEM CLASSIFICATION
        decomposition = await self.generate(
            instruction="""Thoroughly decompose this Bengali math word problem into its semantic and mathematical components. Identify:

1. ALL numerical values and their contextual meaning (e.g., "140" = monthly fee, "10%" = discount rate)
2. Temporal or sequential relationships (e.g., "first half of year", "then", "after")
3. Entities involved (people, objects, services) and their roles
4. Mathematical operations implied by verbs and phrases (e.g., "কম" = subtraction, "অর্ধেক" = division by 2)
5. The ultimate unknown being asked for
6. Any constraints or real-world limitations (e.g., no negative quantities, whole numbers only)

Structure your output clearly with labeled sections. Be exhaustive — do not skip implicit relationships.""",
            context=""
        )

        problem_type = await self.generate(
            instruction=f"""Based on this decomposition:
{decomposition}

Classify the problem into ONE primary type and explain why:
- SEQUENTIAL: Multiple steps in chronological order
- PROPORTIONAL: Involves ratios, percentages, fractions, scaling
- REVERSE_ENGINEERING: Must work backwards from result to initial state
- DISTRIBUTION: Dividing, sharing, allocating quantities
- MULTI_ENTITY: Tracking different quantities across multiple entities

Also identify required mathematical operations and potential pitfalls (unit conversion, hidden steps, etc.).

Output format:
TYPE: [type name]
REASON: [brief justification]
OPERATIONS: [list of operations needed]
PITFALLS: [list of potential errors to avoid]""",
            context=decomposition
        )

        # Extract type for branching (simple string parsing)
        problem_category = "SEQUENTIAL"  # default
        if "TYPE:" in problem_type:
            type_line = [line for line in problem_type.split('\n') if line.startswith("TYPE:")][0]
            problem_category = type_line.split(":", 1)[1].strip().upper()

        # PHASE 2: PARALLEL SOLUTION GENERATION (ADAPTIVE BRANCHING)
        # Generate 2-3 solution attempts based on problem type
        solution_attempts = []

        # Always include a direct computational approach
        direct_computation = asyncio.create_task(
            self.programmer(
                instruction=f"""Solve this problem by direct computation. Use the decomposition:
{decomposition}

Write Python code that:
1. Defines all known values as variables with clear names
2. Performs calculations step by step
3. Prints ONLY the final numerical answer (no text, no units)
4. Includes comments explaining each step

Ensure unit consistency and validate intermediate results.""",
                context=decomposition
            )
        )
        solution_attempts.append(direct_computation)

        # Branch based on problem type
        if "REVERSE" in problem_category or "DISTRIBUTION" in problem_category:
            backward_reasoning = asyncio.create_task(
                self.generate(
                    instruction=f"""Solve by working backwards from the given result or remainder. Use this decomposition:
{decomposition}

Start from the final state mentioned in the problem and reverse-engineer the initial conditions. Show each reverse step clearly. End with the final numerical answer in this format:
ANSWER: [number]""",
                    context=decomposition
                )
            )
            solution_attempts.append(backward_reasoning)
        elif "PROPORTIONAL" in problem_category or "SEQUENTIAL" in problem_category:
            equation_based = asyncio.create_task(
                self.programmer(
                    instruction=f"""Model this as an algebraic equation. Use the decomposition:
{decomposition}

Define variables for unknowns. Set up equations based on relationships described. Solve symbolically first, then numerically. Output ONLY the final number.""",
                    context=decomposition
                )
            )
            solution_attempts.append(equation_based)
        else:
            # Fallback: step-by-step natural language reasoning
            step_by_step = asyncio.create_task(
                self.generate(
                    instruction=f"""Solve step by step in natural language. Use this decomposition:
{decomposition}

For each step:
1. State what you're calculating
2. Show the calculation
3. Give the intermediate result
4. Explain why this step is necessary

End with: FINAL ANSWER: [number]""",
                    context=decomposition
                )
            )
            solution_attempts.append(step_by_step)

        # Add a "unit and sanity check" branch always
        sanity_check = asyncio.create_task(
            self.generate(
                instruction=f"""Perform a sanity check on potential solutions. Consider:
- Real-world plausibility (no negative people, fractional items if not allowed)
- Unit consistency (all calculations in same units)
- Order of magnitude (is the answer reasonable given inputs?)
- Cross-verification with alternative approach

Based on decomposition:
{decomposition}

What range should the answer fall in? What would indicate an error?""",
                context=decomposition
            )
        )
        solution_attempts.append(sanity_check)

        # Gather all parallel attempts
        all_results = await asyncio.gather(*solution_attempts)

        # PHASE 3: ENSEMBLE, VALIDATE, AND REFINE
        final_answer = await self.ensemble(
            instruction="""Synthesize all solution attempts below. Your goal: produce ONE correct numerical answer.

For each attempt:
1. Extract the numerical answer (ignore text/explanations)
2. Verify it against sanity checks and real-world constraints
3. Check for calculation errors or logical flaws
4. Prefer answers that show step-by-step work and unit consistency

If answers conflict:
- Trust the approach most aligned with problem type
- Prefer programmer outputs for precision
- Eliminate answers violating constraints (negative, fractional when inappropriate)

Output ONLY the final number, nothing else.""",
            contexts_list=all_results
        )

        # Final refinement: extract pure number and validate format
        cleaned_answer = await self.revise(
            instruction="""Extract ONLY the numerical answer from the text below. Remove any units, labels, punctuation, or explanatory text. If multiple numbers, pick the one that matches the problem's request. If no clear number, return 0.

Ensure output is a valid number (integer or decimal) with no additional characters.""",
            context=final_answer
        )

        # Simple regex to extract number (handles integers and decimals)
        match = re.search(r'[-+]?\d*\.?\d+', cleaned_answer.replace(',', ''))
        if match:
            return match.group(0)
        else:
            # Fallback: return as-is if no number found (let evaluation handle it)
            return cleaned_answer.strip()