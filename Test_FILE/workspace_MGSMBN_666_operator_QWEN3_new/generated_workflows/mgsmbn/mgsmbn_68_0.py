# Workflow ID: mgsmbn_68_0
# Benchmark: mgsmbn
# Data Indices: [149, 35]

import asyncio

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

        # Step 1: Decompose the problem into structured subproblems
        decomposition = await self.decompose(
            instruction="""Break down this Bengali math word problem into fundamental components. Identify:
            1. All entities (people, objects, places) and their roles
            2. All numerical values and what they represent (initial quantities, rates, totals, etc.)
            3. All actions or events that change quantities (buying, selling, moving, comparing, etc.)
            4. All relationships or constraints (ratios, proportions, inequalities, equalities)
            5. The ultimate unknown we need to solve for
            Format each subproblem as a clear, standalone question that, if answered, would contribute to solving the main problem.
            Prioritize chronological or causal ordering where applicable.""",
            context=""
        )

        # Step 2: Parallel interpretation paths
        literal_path = await self.generate(
            instruction="""Extract all explicit numerical values and directly stated operations from the problem.
            - List every number mentioned and its context
            - Identify any explicitly stated arithmetic operations (add, subtract, multiply, divide)
            - Do not infer or interpret; only extract what is literally present
            - Format as a series of equations or assignments""",
            context=""
        )

        semantic_path = await self.generate(
            instruction="""Interpret all relational and comparative phrases in the problem as mathematical constraints.
            - Phrases like 'অর্ধেকের বেশি' (more than half), 'দ্বিগুণ' (double), 'কম' (less), 'বেশি' (more) must be converted to inequalities or equations
            - Handle proportional relationships (ratios, fractions, percentages)
            - Identify implicit operations (e.g., 'তুলেছেন' implies addition to a total, 'খরচ করেছেন' implies subtraction)
            - Express everything as mathematical expressions with variables for unknowns""",
            context=""
        )

        narrative_path = await self.generate(
            instruction="""Model the problem as a sequence of state changes over time.
            - Identify the initial state (quantities at start)
            - List each action/event in chronological order and how it changes quantities
            - Identify the final state (quantities at end)
            - Express as a series of state transitions: State0 → Action1 → State1 → Action2 → State2 → ... → FinalState
            - The unknown should be a variable in one of these transitions""",
            context=""
        )

        # Step 3: Revise each path for consistency and completeness
        revised_literal = await self.revise(
            instruction=f"""Improve the literal extraction by:
            - Ensuring all numbers from the original problem are accounted for
            - Adding units (টাকা, আপেল, নোট, etc.) to each quantity
            - Flagging any quantities that seem inconsistent or ambiguous
            - If any number is mentioned but not used, explain why
            Original literal extraction: {literal_path}""",
            context=literal_path
        )

        revised_semantic = await self.revise(
            instruction=f"""Refine the semantic interpretation by:
            - Ensuring all comparative phrases are mathematically represented
            - Checking that inequalities are directionally correct (e.g., 'more than half' → > 0.5x)
            - Adding boundary conditions (e.g., quantities can't be negative, must be integers if counting objects)
            - Resolving ambiguities by choosing the most contextually plausible interpretation
            Original semantic interpretation: {semantic_path}""",
            context=semantic_path
        )

        revised_narrative = await self.revise(
            instruction=f"""Enhance the narrative state model by:
            - Verifying chronological order of events
            - Ensuring conservation of quantities (what goes in must come out, unless specified otherwise)
            - Adding explicit mathematical operations for each state transition
            - Identifying which transition contains the unknown variable to solve for
            Original narrative model: {narrative_path}""",
            context=narrative_path
        )

        # Step 4: Ensemble synthesis with validation criteria
        synthesized = await self.ensemble(
            instruction="""Synthesize the three revised interpretations into a single coherent mathematical model.
            Evaluation criteria:
            1. Mathematical consistency: All equations and inequalities must be solvable and non-contradictory
            2. Narrative plausibility: The model must align with the story's sequence of events
            3. Unit consistency: All quantities must have appropriate units and operations must respect unit rules
            4. Domain constraints: No fractional people/objects, no negative quantities unless explicitly allowed
            5. Completeness: Must account for all numbers and relationships in the original problem
            If interpretations conflict, prioritize the narrative path for sequence, semantic path for relationships, and literal path for raw numbers.
            Output a single unified set of equations or steps that can be executed to find the answer.""",
            contexts_list=[revised_literal, revised_semantic, revised_narrative]
        )

        # Step 5: Generate executable code and validate
        code_result = await self.programmer(
            instruction=f"""Generate Python code to solve the mathematical model from the synthesis.
            Requirements:
            - Use only basic arithmetic operations
            - Define all variables explicitly
            - Include comments explaining each step in relation to the problem
            - Validate that the answer meets all constraints (non-negative, integer if counting objects, etc.)
            - If validation fails, adjust assumptions (e.g., round up/down, reinterpret ambiguous phrases) and retry
            - Output only the final numerical answer as a single value
            Synthesized model: {synthesized}""",
            context=synthesized,
            max_retries=3
        )

        # Step 6: Extract final answer (robust parsing)
        # Look for the last number in the output, as programmer should output only the answer
        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', code_result)
        if numbers:
            final_answer = numbers[-1]  # Last number is likely the answer
            # Ensure it's properly formatted (no extra decimals if integer)
            if '.' in final_answer:
                final_answer = final_answer.rstrip('0').rstrip('.')
            return final_answer
        else:
            # Fallback: return the raw programmer output if no number found
            return code_result.strip()