# Workflow ID: mgsmbn_120_0
# Benchmark: mgsmbn
# Data Indices: [10]

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

        # PHASE 1: PARALLEL PROBLEM FINGERPRINTING
        # Generate three independent analyses to capture different dimensions
        classification, entity_extraction, constraint_analysis = await asyncio.gather(
            self.generate(
                instruction="""Comprehensively classify this Bengali math word problem:
                1. Problem Type: Sequential, Rate, Proportional, Distribution, Comparison, or Multi-entity?
                2. Mathematical Operations Required: List all operations (addition, %, ratio, etc.)
                3. Hidden Steps: Are there unstated calculations needed?
                4. Unit Types: Identify all units (টাকা, ঘণ্টা, জিনিস, etc.) and potential conversions
                5. Answer Format: Expected numerical type (integer, decimal, percentage)
                6. Real-world Constraints: Any physical/logical boundaries (non-negative, whole numbers only)
                Present as structured bullet points with clear labels.""",
                context=""
            ),
            self.generate(
                instruction="""Extract all mathematical entities and relationships:
                - List every named quantity with its value and description
                - Map relationships between quantities (e.g., "A is twice B", "C is 25% of D")
                - Identify referents for percentages and fractions (what is the base?)
                - Flag any ambiguous or missing information
                Format as: Entity: [name] = [value] ([description]), Relationship: [A] [relation] [B]""",
                context=""
            ),
            self.generate(
                instruction="""Analyze constraints and boundary conditions:
                - What must the answer satisfy to be physically/logically valid?
                - Are there implicit constraints (e.g., people count must be integer, money non-negative)?
                - What would constitute an obviously wrong answer?
                - Are there multiple possible interpretations? If so, list them.
                Structure as: Constraint: [description] | Validation Rule: [how to check]""",
                context=""
            )
        )

        # PHASE 2: SYNTHESIZE PROBLEM REPRESENTATION
        problem_model = await self.ensemble(
            instruction="""Synthesize the three analyses into a unified problem representation:
            1. Combine classification, entities, and constraints into one coherent model
            2. Resolve any contradictions between analyses
            3. Prioritize the most reliable information from each source
            4. Explicitly state any assumptions made
            5. Output format: 
               PROBLEM TYPE: [type]
               ENTITIES: [list]
               RELATIONSHIPS: [list]
               CONSTRAINTS: [list]
               SOLUTION APPROACH: [recommended method]""",
            contexts_list=[classification, entity_extraction, constraint_analysis]
        )

        # PHASE 3: PARALLEL SOLUTION GENERATION
        # Generate three different solution approaches
        algebraic_solution, arithmetic_solution, proportional_solution = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using ALGEBRAIC approach:
                Given problem model: {problem_model}
                
                Steps:
                1. Define variables for unknowns
                2. Set up equations based on relationships
                3. Solve step-by-step showing all algebraic manipulations
                4. Verify solution against constraints
                5. Box final answer
                
                Special attention to: Unit consistency, percentage base clarity, and real-world validity.""",
                context=problem_model
            ),
            self.generate(
                instruction=f"""Solve using ARITHMETIC approach:
                Given problem model: {problem_model}
                
                Steps:
                1. Perform calculations in chronological/logical order
                2. Show intermediate results with units
                3. Handle percentages as fractions (e.g., 20% = 0.20)
                4. Double-check operations for unit compatibility
                5. Verify against constraints
                6. Box final answer
                
                Focus on: Step-by-step numerical computation without variables.""",
                context=problem_model
            ),
            self.generate(
                instruction=f"""Solve using PROPORTIONAL REASONING approach:
                Given problem model: {problem_model}
                
                Steps:
                1. Identify ratios, proportions, or percentage relationships
                2. Set up proportion equations or scale factors
                3. Solve by cross-multiplication or equivalent fractions
                4. Check that proportions maintain unit consistency
                5. Validate against constraints
                6. Box final answer
                
                Emphasize: Ratio preservation and percentage base identification.""",
                context=problem_model
            )
        )

        # PHASE 4: REVISE SOLUTIONS FOR CONSISTENCY
        revised_solutions = await asyncio.gather(
            self.revise(
                instruction="""Improve this solution:
                - Verify all calculations are mathematically correct
                - Ensure units are tracked consistently throughout
                - Check that percentages are applied to correct bases
                - Confirm answer satisfies all constraints
                - Improve clarity of step-by-step reasoning
                - Fix any logical gaps or unsupported assumptions""",
                context=algebraic_solution
            ),
            self.revise(
                instruction="""Improve this solution:
                - Verify all calculations are mathematically correct
                - Ensure units are tracked consistently throughout
                - Check that percentages are applied to correct bases
                - Confirm answer satisfies all constraints
                - Improve clarity of step-by-step reasoning
                - Fix any logical gaps or unsupported assumptions""",
                context=arithmetic_solution
            ),
            self.revise(
                instruction="""Improve this solution:
                - Verify all calculations are mathematically correct
                - Ensure units are tracked consistently throughout
                - Check that percentages are applied to correct bases
                - Confirm answer satisfies all constraints
                - Improve clarity of step-by-step reasoning
                - Fix any logical gaps or unsupported assumptions""",
                context=proportional_solution
            )
        )

        # PHASE 5: ENSEMBLE BEST SOLUTION
        first_ensemble = await self.ensemble(
            instruction="""Select the best solution or synthesize from multiple:
            Criteria:
            1. Mathematical correctness (highest priority)
            2. Clarity of reasoning steps
            3. Proper unit handling
            4. Constraint satisfaction
            5. Alignment with problem type
            
            If solutions conflict, identify why and choose the most robust.
            If multiple are valid, synthesize the clearest explanation.
            Output only the final solution with boxed answer.""",
            contexts_list=revised_solutions
        )

        # PHASE 6: VALIDATION AND POTENTIAL REVISION
        validation = await self.generate(
            instruction=f"""Critically validate this solution:
            {first_ensemble}
            
            Check:
            1. Are all calculations arithmetically correct?
            2. Are units consistent and properly converted?
            3. Are percentages applied to correct bases?
            4. Does answer satisfy real-world constraints?
            5. Is the reasoning logically sound?
            6. Are there any hidden steps missed?
            
            If any issues found, describe them specifically. Otherwise, output 'VALID'.""",
            context=first_ensemble
        )

        final_solution = first_ensemble
        if "VALID" not in validation.upper():
            # Revise based on validation feedback
            final_solution = await self.revise(
                instruction=f"""Fix the solution based on this validation feedback:
                {validation}
                
                Requirements:
                - Address all identified issues
                - Maintain clear step-by-step reasoning
                - Ensure mathematical correctness
                - Preserve unit consistency
                - Output only the corrected solution with boxed answer""",
                context=first_ensemble
            )

        # PHASE 7: EXTRACT NUMERICAL ANSWER
        answer = await self.generate(
            instruction=f"""Extract ONLY the numerical answer from this solution:
            {final_solution}
            
            Rules:
            1. Return ONLY the number (integer or decimal)
            2. Remove any units, labels, or explanatory text
            3. If answer is percentage, return the number without % symbol
            4. If multiple numbers, return the final answer
            5. Verify it's non-negative if context requires
            6. Round appropriately if decimal
            
            Example outputs: "42", "15.5", "0", "100" """,
            context=final_solution
        )

        # Clean the answer (remove any non-numeric characters)
        cleaned_answer = re.sub(r'[^\d.-]', '', answer.strip())
        
        return cleaned_answer