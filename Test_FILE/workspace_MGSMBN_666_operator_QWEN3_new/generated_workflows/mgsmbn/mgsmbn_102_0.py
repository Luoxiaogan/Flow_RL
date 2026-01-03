# Workflow ID: mgsmbn_102_0
# Benchmark: mgsmbn
# Data Indices: [132, 44]

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

        # PHASE 1: COGNITIVE TRIAGE & PARALLEL HYPOTHESIS GENERATION
        decomposition = await self.decompose(
            instruction="""Break down this Bengali math problem into atomic subproblems. For each subproblem:
            - Identify the mathematical operation required (addition, percentage, ratio, etc.)
            - Extract all numerical values and their semantic roles (base value, rate, time, etc.)
            - Note units and constraints (e.g., 'টাকা', 'জিনিস', integer-only)
            - Flag any ambiguous phrasing or missing information
            - Specify dependencies between subproblems
            Output as structured subproblem list with clear IDs and dependency chains.""",
            context=""
        )

        # Generate three parallel interpretations
        literal_analysis, model_analysis, constraint_analysis = await asyncio.gather(
            self.generate(
                instruction="""Perform literal extraction:
                - List all numbers and their immediate context
                - Identify action verbs (বৃদ্ধি, ভাগ, খরচ, etc.) and map to operations
                - Extract explicit relationships (per, after, total, remaining)
                - Do not interpret, just transcribe and tag""",
                context=""
            ),
            self.generate(
                instruction="""Build mathematical model:
                - Convert the problem into equations or step-by-step procedures
                - Identify growth patterns (linear, exponential, compound)
                - Map qualitative terms to quantitative categories (e.g., 'খারাপ' → defective, 'ভালো' → good)
                - Propose variable names for unknowns
                - Suggest formulaic approaches (percentage change, distribution, etc.)""",
                context=""
            ),
            self.generate(
                instruction="""Analyze constraints and units:
                - List all units and ensure consistency (convert if needed)
                - Identify real-world constraints (no negative people, integer items, etc.)
                - Flag any physically impossible scenarios
                - Note boundary conditions (minimum/maximum values)""",
                context=""
            )
        )

        # PHASE 2: CANONICAL SYNTHESIS
        canonical_representation = await self.ensemble(
            instruction="""Synthesize these three analyses into one canonical problem representation:
            - Resolve contradictions: prioritize mathematical model unless contradicted by unit/constraint analysis
            - Explicitly state all operations in chronological/logical order
            - Annotate each step with units and constraints
            - Replace ambiguous terms with precise mathematical equivalents
            - Output as a numbered step-by-step procedure with clear inputs and outputs for each step""",
            contexts_list=[literal_analysis, model_analysis, constraint_analysis]
        )

        # PHASE 3: MENTAL SIMULATION & VERIFICATION
        verified_plan = await self.revise(
            instruction="""Simulate solving this step-by-step:
            - Mentally execute each step as an elementary student would
            - Check for common errors: off-by-one, misapplied percentages, unit mismatches
            - Verify intermediate results make sense (e.g., price shouldn't drop when increasing)
            - If any step seems ambiguous or error-prone, add clarifying notes
            - Ensure final answer format matches problem requirements (integer, decimal, units)""",
            context=canonical_representation
        )

        # PHASE 4: CODED EXECUTION WITH PEDAGOGICAL CONSTRAINTS
        code_result = await self.programmer(
            instruction="""Generate Python code that mirrors the verified step-by-step plan:
            - Use iterative calculations (not closed-form formulas) to match elementary reasoning
            - Include assertions for unit consistency and boundary checks
            - For percentages, show each compounding step explicitly
            - For distributions, use integer arithmetic with remainders
            - Output only the final numerical answer, no explanations
            - If problem involves discrete items, ensure integer outputs via rounding only if context allows""",
            context=verified_plan,
            max_retries=2
        )

        # PHASE 5: SANITY CHECK & FALLBACK
        sanity_check = await self.generate(
            instruction=f"""Evaluate this answer in real-world context:
            Problem: {self.problem_text}
            Proposed Answer: {code_result}
            
            Does this answer make sense?
            - Are units appropriate? (e.g., no fractional people)
            - Is magnitude reasonable? (e.g., price after 36 months shouldn't be 1000x)
            - Does it satisfy all constraints from earlier analysis?
            If not, suggest a corrected integer value or flag as invalid.""",
            context=code_result
        )

        if "invalid" in sanity_check.lower() or "doesn't make sense" in sanity_check.lower():
            # Fallback: Order-of-magnitude estimation + integer selection
            estimations = await asyncio.gather(
                self.generate(instruction="Estimate answer using rounding to nearest 10...", context=""),
                self.generate(instruction="Estimate using proportional scaling...", context=""),
                self.generate(instruction="Estimate by simplifying percentages to fractions...", context="")
            )
            
            final_answer = await self.ensemble(
                instruction="""Select the most reasonable integer answer from these estimations.
                Prioritize values that:
                - Are whole numbers if problem involves discrete items
                - Match order of magnitude from original calculation
                - Satisfy obvious constraints (e.g., can't exceed total items)
                Output ONLY the numerical value, nothing else.""",
                contexts_list=estimations
            )
        else:
            final_answer = code_result

        # Extract numerical answer from any text
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", final_answer)
        return numbers[0] if numbers else "0"