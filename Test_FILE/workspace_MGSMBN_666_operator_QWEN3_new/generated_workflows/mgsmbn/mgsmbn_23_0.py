# Workflow ID: mgsmbn_23_0
# Benchmark: mgsmbn
# Data Indices: [118, 190]

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

        # PHASE 1: META-COGNITIVE CLASSIFICATION & STRUCTURED EXTRACTION
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this Bengali math word problem. Extract and categorize:

1. ENTITIES: List all objects, people, quantities with their roles (e.g., "John - farmer", "10 hectares - area", "100 pineapples/hectare - yield rate")
2. ACTIONS & RELATIONSHIPS: What operations or changes occur? (e.g., "harvests every 3 months", "money triples after one year")
3. CONSTRAINTS: Explicit and implicit limits (e.g., "one year = 12 months", "apples must be whole numbers")
4. GOAL: What is being asked? Format as "Find: [quantity] [unit]"
5. PROBLEM TYPE: Classify as one of: Sequential, Rate, Proportional, Distribution, Comparison, Multi-entity, or Hybrid

Output in STRICT JSON-like format with keys: entities, actions, constraints, goal, problem_type. No markdown, no explanations.""",
            context=""
        )

        # PHASE 2: PARALLEL REASONING TRACKS
        math_model_task = self.generate(
            instruction=f"""Based on extracted structure:
{problem_analysis}

Generate a precise mathematical model. Translate relationships into equations or computational steps. Include:
- Variables and their meanings
- Sequence of operations (step-by-step)
- Intermediate calculations needed
- Final formula for the answer

Be explicit about order of operations and dependencies. If time-based, convert to consistent units (e.g., months to years).""",
            context=problem_analysis
        )

        temporal_logic_task = self.generate(
            instruction=f"""Based on extracted structure:
{problem_analysis}

Analyze temporal or logical sequencing. Answer:
- What events happen in what order?
- Are there implicit time conversions? (e.g., "every 3 months" in a year = 4 cycles)
- What are the dependencies between steps?
- Could any step be misinterpreted chronologically?

Output as numbered steps with justifications.""",
            context=problem_analysis
        )

        constraint_validation_task = self.generate(
            instruction=f"""Based on extracted structure:
{problem_analysis}

Validate real-world and mathematical constraints:
- Are units consistent? (e.g., mixing hours and minutes)
- Are quantities physically possible? (e.g., negative people, fractional discrete items)
- Are there hidden constraints from context? (e.g., "children" implies whole numbers)
- Does the goal make sense given the inputs?

Flag any potential issues with specific recommendations for adjustment.""",
            context=problem_analysis
        )

        # RUN PARALLEL TRACKS
        math_model, temporal_logic, constraint_validation = await asyncio.gather(
            math_model_task, temporal_logic_task, constraint_validation_task
        )

        # PHASE 3: CONSENSUS BUILDING & CONFLICT RESOLUTION
        synthesis = await self.ensemble(
            instruction="""Synthesize the three analyses (mathematical, temporal, constraint). Your task:

1. Identify points of agreement - these form the core solution.
2. Identify conflicts or discrepancies - these require resolution.
3. For conflicts: generate a reconciliation strategy that references the original problem text.
4. Output a unified solution plan that incorporates all validated insights.

Format:
AGREEMENTS:
- [list]

CONFLICTS:
- [list with reconciliation strategy]

UNIFIED PLAN:
- [step-by-step plan incorporating resolutions]""",
            contexts_list=[math_model, temporal_logic, constraint_validation]
        )

        # PHASE 4: ITERATIVE REFINEMENT LOOP (max 3 iterations)
        current_plan = synthesis
        for iteration in range(3):
            validation = await self.generate(
                instruction=f"""Critically validate this solution plan against the original problem:
{current_plan}

Check for:
- Mathematical accuracy
- Temporal/logical consistency
- Constraint adherence
- Alignment with problem goal

If no issues, output "VALID". If issues found, describe them concisely and suggest specific fixes.""",
                context=current_plan
            )
            
            if "VALID" in validation.upper() and "ISSUE" not in validation.upper() and "ERROR" not in validation.upper():
                break
            else:
                current_plan = await self.revise(
                    instruction=f"""Revise the solution plan to fix these issues:
{validation}

Incorporate fixes while preserving correct elements. Maintain step-by-step structure and explicit reasoning.""",
                    context=current_plan
                )

        # PHASE 5: CODE GENERATION WITH ASSERTIONS
        code_result = await self.programmer(
            instruction=f"""Generate Python code to compute the final answer based on this validated plan:
{current_plan}

Requirements:
- Include explicit variable assignments for all known values
- Add assertions to validate key assumptions (e.g., assert harvests_per_year == 4)
- Handle edge cases mentioned in constraints (e.g., rounding for discrete items)
- Output ONLY the final numerical answer (no text, no units)
- Use exact arithmetic (no floating point unless necessary)

Example structure:
# Known values from problem
hectares = 10
yield_per_hectare = 100
harvests_per_year = 4  # from temporal analysis

# Assertions for validation
assert harvests_per_year == 4, "Harvests per year must be 4 based on 'every 3 months' in 12-month year"

# Calculation
total = hectares * yield_per_hectare * harvests_per_year
print(total)""",
            context=current_plan
        )

        # PHASE 6: FINAL EXTRACTION & SANITIZATION
        # Extract just the numerical answer from code output
        answer_match = re.search(r'[-+]?\d*\.\d+|\d+', code_result)
        if answer_match:
            final_answer = answer_match.group(0)
            # Convert to int if whole number
            if '.' in final_answer and final_answer.endswith('.0'):
                final_answer = final_answer[:-2]
            return final_answer
        else:
            # Fallback: return raw code result if parsing fails
            return code_result.strip()