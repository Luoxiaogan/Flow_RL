# Workflow ID: mgsmbn_91_0
# Benchmark: mgsmbn
# Data Indices: [174, 166]

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

        # PHASE 1: Linguistic Decomposition & Entity Mapping
        decomposition = await self.decompose(
            instruction="""Thoroughly decompose this Bengali math word problem into structured subproblems. For each subproblem:
            - Identify all numerical values and what they represent (e.g., '4টি গোলাপ' → quantity=4, entity=roses)
            - Extract all relationships (e.g., '7টি ডালিয়া বেশি' → daisies = roses + 7)
            - Note temporal sequences (e.g., 'সোমবার... মঙ্গলবার...' → ordered steps)
            - Flag comparative terms ('বেশি', 'কম', 'গুণ') and proportional indicators
            - Identify the final target (what is being asked)
            - Preserve units (টাকা, ঘণ্টা, জিনিস, etc.)
            Output as a numbered list of subproblems with clear dependencies.""",
            context=""
        )

        # Summarize decomposition for downstream use
        decomposition_summary = await self.summarize(
            instruction="""Condense the decomposition into a single paragraph highlighting:
            - Key entities and their initial values
            - Core mathematical relationships
            - Sequence of operations (if any)
            - Final target variable
            Format: 'Entities: [list]. Relationships: [list]. Target: [variable]'""",
            context=str(decomposition)
        )

        # PHASE 2: Problem Classification & Strategy Selection
        problem_type = await self.generate(
            instruction=f"""Classify this problem based on its mathematical structure:
            - Additive (involving sums, differences, comparisons like 'বেশি/কম')
            - Multiplicative (involving products, ratios, 'গুণ', fractions)
            - Sequential (multiple steps over time or conditions)
            - Proportional (percentages, scaling, distributions)
            - Hybrid (combination of above)
            
            Also determine:
            - Required operations (addition, subtraction, multiplication, division, combination)
            - Whether intermediate steps are explicitly stated or implied
            - Expected answer format (integer, decimal, unit-constrained)
            
            Output as: 'Type: [type]. Operations: [list]. Steps: [explicit/implied]. Format: [integer/decimal]'""",
            context=decomposition_summary
        )

        # PHASE 3: Parallel Solution Generation
        # Path 1: Symbolic Reasoning
        symbolic_solution = await self.generate(
            instruction=f"""Solve using symbolic mathematical reasoning:
            - Represent entities as variables (e.g., roses = 4, daisies = roses + 7)
            - Write equations for each relationship
            - Solve step by step, showing substitutions
            - Track units throughout
            - Box final answer as \\boxed{{value}}
            Context: {decomposition_summary}""",
            context=decomposition_summary
        )

        # Path 2: Code Generation
        code_solution = await self.programmer(
            instruction=f"""Generate Python code to solve this problem:
            - Define variables with descriptive names based on Bengali entities
            - Implement all mathematical relationships as code operations
            - Include comments explaining each step in English
            - Print only the final numerical answer (no text)
            - Handle edge cases (negative results, division by zero)
            Context: {decomposition_summary}""",
            context=decomposition_summary
        )

        # Path 3: Arithmetic Tracing
        arithmetic_solution = await self.generate(
            instruction=f"""Solve by explicit arithmetic tracing:
            - List each calculation step chronologically
            - Show intermediate results with units
            - Justify each operation based on problem text
            - Verify no steps are skipped
            - Final answer must be isolated and boxed as \\boxed{{value}}
            Context: {decomposition_summary}""",
            context=decomposition_summary
        )

        # PHASE 4: Ensemble Synthesis & Validation
        solutions = [symbolic_solution, code_solution, arithmetic_solution]
        ensemble_result = await self.ensemble(
            instruction="""Synthesize the three solutions:
            - Compare numerical outputs. If all match, output the consensus.
            - If two match and one differs, explain the discrepancy and select majority.
            - If all differ, flag 'REANALYZE' and suggest likely error sources.
            - Ensure answer is non-negative and unit-appropriate (no fractional people/objects unless specified).
            - Output ONLY the final numerical value (no units, no text).""",
            contexts_list=solutions
        )

        # PHASE 5: Validation & Self-Correction Loop
        validated_result = await self.revise(
            instruction="""Validate the answer:
            - Is it non-negative? (unless context allows negatives)
            - Does it match expected format (integer/decimal)?
            - Is it plausible in real-world context? (e.g., no 0.5 people)
            - Does it satisfy all problem constraints?
            If any check fails, regenerate with: 'ERROR: [reason]. REGENERATE with strict constraints.'
            Otherwise, output the numerical value unchanged.""",
            context=ensemble_result
        )

        # Extract final numerical answer
        # Handle cases where validation might have added text
        match = re.search(r'(\d+\.?\d*)', validated_result)
        if match:
            return match.group(1)
        else:
            # Fallback: return ensemble result if validation failed to extract number
            match = re.search(r'(\d+\.?\d*)', ensemble_result)
            return match.group(1) if match else "0"