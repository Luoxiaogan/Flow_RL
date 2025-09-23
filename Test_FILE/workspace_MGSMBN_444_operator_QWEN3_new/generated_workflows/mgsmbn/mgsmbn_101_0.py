# Workflow ID: mgsmbn_101_0
# Benchmark: mgsmbn
# Data Indices: [85, 107]

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

        # PHASE 1: Deep Semantic Decomposition
        # Extract entities, quantities, relationships, and constraints
        decomposition = await self.generate(
            instruction="""Perform comprehensive semantic decomposition of the Bengali math problem. Structure your output EXACTLY as follows:

[ENTITIES]
- List all named entities (people, objects, containers) with their roles
- For each entity, note initial state, actions performed, and final state

[QUANTITIES]
- List all numerical values with their semantic meaning (e.g., "5 inches = external length")
- Group related quantities (e.g., dimensions of same object)

[RELATIONSHIPS]
- Map dependencies between entities and quantities
- Note comparative relationships (more than, less than, equal to)
- Identify sequential or temporal relationships

[CONSTRAINTS]
- Explicit constraints stated in problem
- Implicit physical/logical constraints (e.g., wall thickness affects internal dimensions)
- Unit consistency requirements

[UNKNOWN]
- Precisely state what is being asked for
- Note expected answer format (integer, decimal, unit)

Be exhaustive. Do not solve yet — only model the problem structure.""",
            context=""
        )

        # PHASE 2: Parallel Solution Path Generation
        # Generate 3 distinct solution approaches in parallel
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Generate SOLUTION PATH 1: Literal Interpretation
Using the decomposition: {decomposition}

- Follow the problem text step-by-step literally
- Perform calculations in chronological order as described
- Show all intermediate steps with units
- Do not make assumptions beyond what's explicitly stated
- Final answer must be boxed as \\boxed{{answer}}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate SOLUTION PATH 2: Physical/Geometric Modeling
Using the decomposition: {decomposition}

- Focus on physical interpretations (dimensions, volumes, spatial relationships)
- Account for implicit physical constraints (e.g., wall thickness reducing internal space)
- Use geometric formulas where applicable
- Show dimensional analysis and unit conversions
- Final answer must be boxed as \\boxed{{answer}}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate SOLUTION PATH 3: Proportional/Algebraic Reasoning
Using the decomposition: {decomposition}

- Frame as algebraic equations or proportional relationships
- Define variables for unknowns
- Solve symbolically before plugging in numbers
- Check for ratio, percentage, or rate patterns
- Final answer must be boxed as \\boxed{{answer}}""",
                context=decomposition
            )
        )

        # PHASE 3: Parallel Validation & Refinement
        # Revise each solution path with rigorous verification
        refined_paths = []
        for i, path in enumerate(solution_paths):
            refined = await self.revise(
                instruction=f"""CRITICALLY REVISE SOLUTION PATH {i+1}:
1. Verify every arithmetic operation step-by-step
2. Check unit consistency throughout (convert if needed)
3. Validate against constraints from decomposition: {decomposition}
4. Ensure contextual plausibility (no negative volumes, fractional people, etc.)
5. Trace back to original problem — does this answer what was asked?
6. If error found, correct it and explain the fix
7. Preserve \\boxed{{answer}} format for final result""",
                context=path
            )
            refined_paths.append(refined)

        # PHASE 4: Ensemble Synthesis & Selection
        # Choose best solution or synthesize insights
        final_answer = await self.ensemble(
            instruction="""SYNTHESIZE OPTIMAL SOLUTION:
Compare all revised solution paths. Select or synthesize based on:

CRITERIA 1: Constraint Satisfaction
- Must satisfy ALL explicit and implicit constraints from decomposition
- Must handle units correctly throughout
- Must address the exact unknown requested

CRITERIA 2: Mathematical Rigor
- Arithmetic must be flawless
- Steps must be logically sequenced
- No unjustified assumptions

CRITERIA 3: Contextual Plausibility
- Answer must make real-world sense (e.g., positive volume, whole tickets)
- Must align with problem's narrative

If multiple paths are valid, synthesize their strengths into one unified solution.
If paths conflict, select the one with strongest constraint alignment.
If all paths have flaws, choose the least flawed and note residual uncertainty.

OUTPUT FORMAT:
- Begin with "SELECTED SOLUTION: "
- Show final calculation steps
- End with \\boxed{{answer}} on its own line""",
            contexts_list=refined_paths
        )

        # PHASE 5: Fallback Sanity Check
        # Extract numerical answer and validate format
        try:
            # Extract boxed answer using regex
            match = re.search(r'\\boxed\{([^\}]*)\}', final_answer)
            if match:
                raw_answer = match.group(1).strip()
                # Convert to number if possible
                if '.' in raw_answer:
                    answer = float(raw_answer)
                else:
                    answer = int(raw_answer)
                
                # Contextual sanity checks
                if answer < 0:
                    # For problems where negative doesn't make sense
                    if any(term in self.problem_text for term in ['আয়তন', 'টিকিট', 'জিনিস', 'ব্যক্তি']):
                        # Generate fallback using order of magnitude
                        fallback = await self.generate(
                            instruction=f"""SANITY CHECK FAILED: Negative answer {answer} for contextually positive quantity.
Generate fallback solution using order-of-magnitude estimation:
- What's reasonable scale? (e.g., tickets: 10-100, volumes: 10-1000)
- Recalculate ignoring complex steps, focus on dominant terms
- Output only \\boxed{{positive_estimate}}""",
                            context=final_answer
                        )
                        match = re.search(r'\\boxed\{([^\}]*)\}', fallback)
                        if match:
                            answer = float(match.group(1).strip()) if '.' in match.group(1) else int(match.group(1).strip())
            else:
                raise ValueError("No boxed answer found")
        except Exception:
            # Last resort: extract any number from final answer
            numbers = re.findall(r'[-+]?\d*\.\d+|\d+', final_answer)
            if numbers:
                answer = float(numbers[-1]) if '.' in numbers[-1] else int(numbers[-1])
            else:
                answer = 0  # Ultimate fallback

        return answer