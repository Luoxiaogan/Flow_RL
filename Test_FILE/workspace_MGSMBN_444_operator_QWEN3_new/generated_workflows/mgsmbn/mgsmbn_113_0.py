# Workflow ID: mgsmbn_113_0
# Benchmark: mgsmbn
# Data Indices: [116, 51]

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

        # === PHASE 1: SEMANTIC DECOMPOSITION ===
        decomposition = await self.generate(
            instruction="""Perform deep semantic decomposition of this Bengali word problem. Extract and structure:

1. ENTITIES: List all people, objects, or groups mentioned (e.g., 'জর্ডন', 'শিক্ষক', 'ছেলে', 'মেয়ে').
2. QUANTITIES: List all numerical values with their explicit units and what they describe (e.g., '2 ঘণ্টা/দিন', 'প্রতি ঘণ্টায় $10').
3. RELATIONSHIPS: Describe mathematical or logical relationships (e.g., 'ছেলে = 2 × মেয়ে', 'প্রতি শিক্ষকে 5 শিক্ষার্থী').
4. TARGET: Clearly state what is being asked (e.g., 'সপ্তাহে মোট আয়', 'মোট শিক্ষক সংখ্যা').
5. CONSTRAINTS: Note any implicit real-world constraints (e.g., 'শিক্ষক সংখ্যা পূর্ণসংখ্যা হতে হবে').

Format as a structured JSON-like block with clear section headers. Be exhaustive and precise.""",
            context=""
        )

        # === PHASE 2: PROBLEM CLASSIFICATION & STRATEGY SELECTION ===
        classification = await self.generate(
            instruction=f"""Based on the decomposition:
{decomposition}

Classify this problem into exactly one primary archetype:
- SEQUENTIAL: Steps must be performed in chronological order (e.g., deposit then withdraw).
- PROPORTIONAL: Involves ratios, scaling, percentages, or multiplicative relationships.
- DISTRIBUTION: Dividing quantities, equal sharing, or allocation with remainders.
- COMPARISON: Finding differences, "how many more", or relative quantities.
- MULTI-ENTITY: Tracking multiple agents with different values or rates.

Also identify secondary characteristics:
- Requires unit conversion? (e.g., hours to days)
- Involves hidden intermediate steps?
- Has conditional exceptions? (e.g., "except Fridays")

Output format:
ARCHETYPE: [primary]
SECONDARY: [list]
STRATEGY: [1-2 sentence description of recommended solving approach]""",
            context=decomposition
        )

        # === PHASE 3: PARALLEL SOLUTION GENERATION ===
        # Dynamically craft solution instructions based on classification
        archetype = re.search(r'ARCHETYPE:\s*(\w+)', classification)
        archetype = archetype.group(1) if archetype else "GENERAL"

        solution_instructions = {
            "SEQUENTIAL": """Solve step-by-step in strict chronological order. For each step:
- State what is being calculated
- Show the arithmetic operation
- Track units explicitly
- Carry forward intermediate results
Final answer must reflect the cumulative effect of all steps.""",
            
            "PROPORTIONAL": """Use proportional reasoning. Options:
a) Set up and solve an equation (e.g., boys = 2 × girls)
b) Use unit rate method (e.g., earnings per hour × total hours)
c) Apply scaling factor directly
Show all proportional relationships and cross-check with decomposition.""",
            
            "DISTRIBUTION": """Model as division with possible remainders. Steps:
1. Calculate total quantity to distribute
2. Divide by group size or per-unit allocation
3. Handle remainders per problem constraints (ignore? round up?)
4. Verify answer satisfies original conditions.""",
            
            "COMPARISON": """Focus on differences or relative quantities:
- Identify base quantity and compared quantity
- Calculate absolute difference or ratio
- Ensure answer addresses "how many more/less" or "times as many"
- Double-check directionality (A vs B, not B vs A)""",
            
            "MULTI-ENTITY": """Track each entity separately:
- Create a table or list for each agent's quantities
- Calculate individual contributions or states
- Aggregate or compare as required
- Ensure no entity is overlooked""",
            
            "GENERAL": """Apply comprehensive mathematical modeling:
1. Translate Bengali relationships into algebraic expressions
2. Solve step-by-step with explicit intermediate values
3. Verify unit consistency at each step
4. Cross-check final answer against problem constraints"""
        }

        base_instruction = solution_instructions.get(archetype, solution_instructions["GENERAL"])
        
        # Generate 3 parallel solution attempts with varied emphasis
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""{base_instruction}

APPROACH 1: ALGEBRAIC
- Define variables for unknowns
- Write equations based on relationships
- Solve systematically
- Box final numerical answer""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""{base_instruction}

APPROACH 2: UNIT-TRACKING
- Start from given quantities
- Apply operations while preserving units (টাকা, ঘণ্টা, জন)
- Cancel units appropriately
- Final answer must have correct unit dimension""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""{base_instruction}

APPROACH 3: REAL-WORLD SIMULATION
- Imagine physically performing the actions described
- Calculate step-by-step as if experiencing the scenario
- Apply common sense constraints (no negative people, whole teachers)
- Verify answer makes practical sense""",
                context=decomposition
            )
        )

        # === PHASE 4: ADVERSARIAL REVISION ===
        revised_solutions = []
        for i, attempt in enumerate(solution_attempts):
            revision = await self.revise(
                instruction=f"""CRITICALLY REVISE this solution attempt:

1. VERIFY CALCULATIONS: Recompute all arithmetic. Flag any errors.
2. CHECK UNITS: Ensure unit consistency throughout. Convert if needed.
3. VALIDATE LOGIC: Does each step follow from the previous? Any leaps?
4. REAL-WORLD CHECK: Does answer respect constraints? (e.g., integer teachers)
5. ALIGN WITH DECOMPOSITION: Does it use all given quantities and relationships?

If errors found, correct them and explain fixes. If no errors, strengthen explanation.
Output revised solution with clear final answer.""",
                context=attempt
            )
            revised_solutions.append(revision)

        # === PHASE 5: CONSENSUS ENSEMBLE ===
        final_answer = await self.ensemble(
            instruction="""SELECT OR SYNTHESIZE the best final answer:

1. COMPARE all three revised solutions:
   - Do they agree numerically? If yes, output that value.
   - If not, identify which solution has the most rigorous/logical derivation.
2. CHECK FOR OUTLIERS: If two agree and one differs, prefer the majority.
3. FINAL VALIDATION: 
   - Is the answer a single number (integer or decimal)?
   - Does it match the problem's requested unit/dimension?
   - Is it reasonable in magnitude? (e.g., not 1000 teachers for 60 students)
4. OUTPUT: Only the numerical answer, nothing else. No units, no text.

Example output: 140""",
            contexts_list=revised_solutions
        )

        # Extract just the number (defensive parsing)
        number_match = re.search(r'[\d,]+\.?\d*', final_answer.replace(',', ''))
        if number_match:
            return float(number_match.group()) if '.' in number_match.group() else int(number_match.group())
        else:
            # Fallback: return first revised solution's number
            for sol in revised_solutions:
                fallback_match = re.search(r'[\d,]+\.?\d*', sol.replace(',', ''))
                if fallback_match:
                    val = float(fallback_match.group()) if '.' in fallback_match.group() else int(fallback_match.group())
                    return val
            return 0  # Ultimate fallback