# Workflow ID: mgsmbn_114_0
# Benchmark: mgsmbn
# Data Indices: [188, 133]

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

        # === PHASE 1: PARALLEL EXTRACTION (Diamond Fork) ===
        # Extract three core dimensions simultaneously: entities/quantities, relationships/operations, and constraints/context
        entity_extraction, relationship_extraction, constraint_extraction = await asyncio.gather(
            self.generate(
                instruction="""You are a precise mathematical analyst. Extract ALL named entities, quantities, and their roles from the Bengali problem.
                Format STRICTLY as:
                ENTITIES:
                - [Entity Name]: [Quantity] [Unit if any] - [Role/Description]
                Example: 
                - Steve: 6 টি টমেটো - প্রতিদিন খায়
                - Tomato vine: 3 টি টমেটো - প্রতি সপ্তাহে উৎপাদন
                
                Include people, objects, rates, time periods, and any measurable quantities. Do not perform calculations yet.
                """,
                context=""
            ),
            self.generate(
                instruction="""You are a relationship mapper. Identify ALL mathematical relationships, operations, and dependencies between entities.
                Format STRICTLY as:
                RELATIONSHIPS:
                - [Entity A] [Operator] [Entity B] : [Description]
                Example:
                - Steve's consumption = 2 × Friend's consumption : সে তার বান্ধবীর তুলনায় দুইগুণ বেশি খায়
                - Weekly production = Daily consumption × 7 : সপ্তাহে 7 দিন
                
                Include multiplicative, additive, comparative, and temporal relationships. Use symbols (=, ×, +, -, >, <) for clarity.
                """,
                context=""
            ),
            self.generate(
                instruction="""You are a constraint validator. Identify ALL explicit and implicit constraints, units, and real-world boundaries.
                Format STRICTLY as:
                CONSTRAINTS:
                - [Constraint Type]: [Description] - [Why it matters]
                Example:
                - Unit consistency: টমেটো must be in same unit throughout - prevents calculation errors
                - Temporal alignment: প্রতিদিন vs প্রতি সপ্তাহে - requires multiplication by 7
                - Non-negative: Number of vines cannot be negative - real-world constraint
                
                Include unit conversions, time conversions, physical impossibilities, and domain-specific rules.
                """,
                context=""
            )
        )

        # === PHASE 2: SYNTHESIZE INTO UNIFIED MODEL (Diamond Merge) ===
        unified_model = await self.ensemble(
            instruction="""You are a master model integrator. Synthesize the three analyses below into ONE coherent mathematical model.
            Your output must:
            1. Combine entities, relationships, and constraints without contradiction
            2. Resolve any conflicts by prioritizing: dimensional consistency > temporal sequence > explicit statements
            3. Structure as:
               MODEL:
               Knowns:
               - [Entity]: [Value] [Unit] - [Source/Justification]
               Unknowns:
               - [Variable]: [What we solve for] - [Constraints]
               Equations:
               - [Equation 1] : [Derived from relationship]
               - [Equation 2] : [Derived from constraint]
               Solution Path:
               - Step 1: [Action]
               - Step 2: [Action]
               ...
            
            CRITICAL: If any quantity lacks unit, infer from context. If timeline is implied, make explicit.
            """,
            contexts_list=[entity_extraction, relationship_extraction, constraint_extraction]
        )

        # === PHASE 3: GENERATE SOLUTION ATTEMPT ===
        initial_solution = await self.generate(
            instruction=f"""You are a meticulous Bengali math solver. Using ONLY the unified model below, compute the numerical answer.
            MODEL:
            {unified_model}
            
            Requirements:
            - Show ALL calculation steps with intermediate results
            - Convert units explicitly (e.g., পয়সা to টাকা, মিনিট to ঘণ্টা)
            - Maintain full precision until final step
            - If algebra is needed, show equation setup and solving
            - Final answer must be a NUMBER ONLY (no units, no text)
            
            Example output format:
            Calculation:
            1. Weekly consumption = 6 × 7 = 42 টি
            2. Vines needed = 42 ÷ 3 = 14
            3. But Steve eats 2× friend → total = 14 × 1.5 = 21
            Answer: 21
            """,
            context=unified_model
        )

        # === PHASE 4: VALIDATE & REVISE (Iterative Loop) ===
        current_solution = initial_solution
        for iteration in range(3):  # Max 3 refinement cycles
            validation = await self.generate(
                instruction=f"""You are a ruthless validator. Critique the solution below against the original problem.
                Check for:
                1. Mathematical errors (wrong operations, miscalculations)
                2. Unit mismatches or missing conversions
                3. Violated constraints (negative people, fractional items when inappropriate)
                4. Misinterpreted relationships (e.g., "twice as much" as additive not multiplicative)
                5. Chronological errors (operations in wrong order)
                
                If perfect, output "VALID: [reason]". If flawed, output "INVALID: [specific error]".
                
                Solution to validate:
                {current_solution}
                """,
                context=current_solution
            )

            if "VALID" in validation:
                break
            else:
                current_solution = await self.revise(
                    instruction=f"""You are a precision engineer. Fix the solution based EXACTLY on this validation critique:
                    {validation}
                    
                    Preserve correct parts. Only change what's necessary. Maintain step-by-step format.
                    Final answer must still be NUMBER ONLY on last line.
                    """,
                    context=current_solution
                )

        # === PHASE 5: FINAL EXTRACTION & CLEANING ===
        final_answer = await self.revise(
            instruction="""You are a final answer extractor. From the solution below, extract ONLY the numerical answer.
            Rules:
            - Must be integer or decimal number
            - NO units, NO text, NO explanations
            - If multiple numbers, take the last one (final answer)
            - If fractional, convert to decimal if needed
            - Example acceptable outputs: "21", "15.5", "0.75"
            
            Solution:
            """,
            context=current_solution
        )

        # Clean any residual text (defensive programming)
        # Extract first number from string
        match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return as-is (let grading handle it)
            return final_answer.strip()