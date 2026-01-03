# Workflow ID: mgsmbn_40_0
# Benchmark: mgsmbn
# Data Indices: [76, 102]

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

        # Step 1: Parallel Semantic Extraction
        entity_extraction = asyncio.create_task(
            self.generate(
                instruction="""Extract all numerical values and their semantic roles from the problem. 
                For each number, specify:
                - What real-world quantity it represents (e.g., 'volume of sauce', 'number of tomatoes')
                - Its unit (if any)
                - Whether it's an input, output, or intermediate value
                - Any modifiers (e.g., 'half', 'more than', 'per unit')
                Format as a structured list with clear labels.""",
                context=""
            )
        )
        
        relation_extraction = asyncio.create_task(
            self.generate(
                instruction="""Identify all mathematical relationships and operations implied in the problem.
                Look for:
                - Comparative phrases ('more than', 'less than', 'times as many')
                - Proportional indicators ('per', 'for every', 'ratio')
                - Transformation verbs ('becomes', 'reduces to', 'increases by')
                - Temporal sequences ('first', 'then', 'finally')
                Map each relationship to the entities involved and the operation type (additive, multiplicative, etc.).
                Provide a structured mapping.""",
                context=""
            )
        )
        
        constraint_extraction = asyncio.create_task(
            self.generate(
                instruction="""Identify all explicit and implicit constraints:
                - Domain constraints (e.g., 'number of people must be integer', 'money can't be negative')
                - Physical constraints (e.g., 'volume can't exceed container size')
                - Logical constraints (e.g., 'if A > B and B > C, then A > C')
                - Contextual plausibility (e.g., 'a person can't have 1000 siblings')
                List each constraint with its justification and severity (hard vs. soft).""",
                context=""
            )
        )

        # Await parallel extractions
        entities, relations, constraints = await asyncio.gather(
            entity_extraction, relation_extraction, constraint_extraction
        )

        # Step 2: Synthesize Problem Schema
        problem_schema = await self.ensemble(
            instruction="""Synthesize the three analyses into a unified problem schema.
            Combine:
            - The entities and their roles
            - The relationships between them
            - The constraints that apply
            Output a comprehensive problem model that can guide decomposition.
            Structure it as:
            [Entities]
            [Relationships]
            [Constraints]
            [Implied Operations]""",
            contexts_list=[entities, relations, constraints]
        )

        # Step 3: Hierarchical Decomposition
        decomposition = await self.decompose(
            instruction=f"""Break down the problem into ordered subproblems based on the schema:
            {problem_schema}
            
            For each subproblem:
            - Clearly state what needs to be calculated
            - Identify dependencies (which subproblems must be solved first)
            - Specify the mathematical operation or reasoning step required
            - Note any constraints that apply at this step
            Ensure the decomposition reveals any hidden or implicit steps not explicitly stated in the problem.""",
            context=problem_schema
        )

        # Step 4: Problem Type Classification
        problem_type = await self.generate(
            instruction=f"""Based on the decomposition:
            {decomposition}
            
            Classify this problem into one primary archetype:
            - Sequential: Multiple steps in chronological order
            - Proportional: Involves ratios, rates, or scaling
            - Comparative: Involves differences or relative quantities (x and x+k)
            - Multi-entity: Tracking multiple distinct quantities or agents
            - Hybrid: Combination of above
            
            Justify your classification with specific references to the decomposition.
            Output ONLY the classification label (e.g., "Proportional") followed by a colon and brief justification.""",
            context=problem_schema
        )

        # Extract classification label
        classification = problem_type.split(":")[0].strip().lower()

        # Step 5: Strategy-Specific Execution
        if "proportional" in classification:
            solution_approach = await self.generate(
                instruction=f"""Given this is a proportional problem, derive the unit rate or scaling factor.
                From the decomposition:
                {decomposition}
                
                Steps:
                1. Identify the base unit and its associated quantity.
                2. Calculate the rate (quantity per unit).
                3. Apply the rate to the target quantity.
                4. Show the mathematical formula.
                Output the formula and intermediate values clearly.""",
                context=problem_schema
            )
            
            solution = await self.programmer(
                instruction="""Execute the proportional calculation.
                Use the formula provided in the context.
                Ensure unit consistency.
                Round to appropriate decimal places if needed.
                Output only the final numerical result.""",
                context=solution_approach
            )
            
        elif "comparative" in classification:
            solution_approach = await self.generate(
                instruction=f"""Given this is a comparative problem, set up the algebraic relationship.
                From the decomposition:
                {decomposition}
                
                Steps:
                1. Define variables for unknown quantities.
                2. Express relationships as equations (e.g., x + (x+6) = total).
                3. Solve for the unknown.
                4. Show the equation and solution steps.
                Output the equation and solution clearly.""",
                context=problem_schema
            )
            
            solution = await self.programmer(
                instruction="""Execute the algebraic solution.
                Solve the equation provided in the context.
                Ensure the answer satisfies all constraints (e.g., positive, integer if required).
                Output only the final numerical result.""",
                context=solution_approach
            )
            
        elif "sequential" in classification:
            solution_approach = await self.generate(
                instruction=f"""Given this is a sequential problem, outline the step-by-step calculation.
                From the decomposition:
                {decomposition}
                
                Steps:
                1. List operations in chronological order.
                2. Show intermediate results after each step.
                3. Track units throughout.
                4. Verify each step against constraints.
                Output the sequence of calculations clearly.""",
                context=problem_schema
            )
            
            solution = await self.programmer(
                instruction="""Execute the sequential calculations.
                Follow the steps provided in the context.
                Maintain state between steps.
                Output only the final numerical result.""",
                context=solution_approach
            )
            
        elif "multi-entity" in classification:
            solution_approach = await self.generate(
                instruction=f"""Given this is a multi-entity problem, track each entity separately.
                From the decomposition:
                {decomposition}
                
                Steps:
                1. Create a table or list for each entity's quantity.
                2. Apply operations to each entity as specified.
                3. Sum or compare as required.
                4. Validate against constraints for each entity.
                Output the tracking and final aggregation clearly.""",
                context=problem_schema
            )
            
            solution = await self.programmer(
                instruction="""Execute the multi-entity tracking and aggregation.
                Follow the tracking steps provided in the context.
                Ensure no entity violates constraints.
                Output only the final numerical result.""",
                context=solution_approach
            )
            
        else:  # Default or Hybrid
            solution_approach = await self.generate(
                instruction=f"""Apply a general problem-solving approach.
                From the decomposition:
                {decomposition}
                
                Steps:
                1. Identify the target unknown.
                2. Work backwards from the target if needed.
                3. Fill in missing values using relationships.
                4. Show all calculations.
                Output the reasoning and calculations clearly.""",
                context=problem_schema
            )
            
            solution = await self.programmer(
                instruction="""Execute the general solution.
                Follow the reasoning provided in the context.
                Output only the final numerical result.""",
                context=solution_approach
            )

        # Step 6: Validation and Refinement Loop
        for attempt in range(2):  # Max 2 refinement attempts
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                Solution: {solution}
                Constraints: {constraints}
                
                Check:
                - Does the answer satisfy all hard constraints?
                - Is the unit correct and consistent?
                - Is the magnitude plausible in real-world context?
                - Are there any arithmetic errors?
                If any issue is found, describe it specifically. Otherwise, say 'VALID'.""",
                context=solution
            )
            
            if "VALID" in validation or "valid" in validation:
                break
            else:
                solution = await self.revise(
                    instruction=f"""Revise the solution based on this critique:
                    {validation}
                    
                    Steps:
                    1. Address each specific issue raised.
                    2. Recalculate if necessary.
                    3. Ensure all constraints are satisfied.
                    Output the revised numerical result only.""",
                    context=solution
                )

        # Final extraction of numerical answer
        # Use regex to extract the first number (integer or decimal) from the solution string
        match = re.search(r'[-+]?\d*\.\d+|\d+', solution)
        if match:
            final_answer = match.group(0)
        else:
            # Fallback: return the solution as-is if no number found (shouldn't happen)
            final_answer = solution.strip()

        return final_answer