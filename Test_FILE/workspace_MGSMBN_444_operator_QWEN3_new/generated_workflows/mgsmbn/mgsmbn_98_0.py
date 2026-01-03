# Workflow ID: mgsmbn_98_0
# Benchmark: mgsmbn
# Data Indices: [150]

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

        # PHASE 1: PARALLEL SEMANTIC DECOMPOSITION
        # Generate three independent interpretations focusing on different aspects
        entity_extraction, quantity_mapping, constraint_analysis = await asyncio.gather(
            self.generate(
                instruction="""Extract all entities, their groupings, and roles with extreme precision. 
                Identify every noun that represents a countable object or agent (e.g., rats, cages, hamsters, rabbits). 
                For each entity, specify:
                - What it is (species, object, person)
                - How it's grouped (per cage, per person, total)
                - Its relationship to other entities
                - Any modifiers (equal groups, individually, etc.)
                Format as bullet points with clear labels. Resolve ambiguous references by cross-checking the entire text.""",
                context=""
            ),
            self.generate(
                instruction="""Map all numerical values to their exact meanings and operations. 
                For every number mentioned:
                - What does it quantify? (e.g., 6 pieces per rat)
                - What operation does it imply? (multiplication, division, etc.)
                - What is its scope? (applies to which entities/groups?)
                - Is it a total, rate, or individual amount?
                Create a structured table in text form: Number | Meaning | Operation | Scope.
                Pay special attention to distributive phrases like 'প্রত্যেকটি' (each) or 'মোট' (total).""",
                context=""
            ),
            self.generate(
                instruction="""Identify all constraints, conditions, and boundaries. 
                Look for:
                - Explicit totals or limits (e.g., 160 pieces total)
                - Implicit constraints (e.g., can't have negative animals)
                - Category boundaries (e.g., rodents vs. rabbits)
                - Distribution rules (equal sharing, individual allocation)
                - Temporal or sequential dependencies
                List each constraint with its source phrase from the text and its mathematical implication.
                Flag any potential ambiguities or missing information.""",
                context=""
            )
        )

        # PHASE 2: ENSEMBLE INTO UNIFIED MODEL
        unified_model = await self.ensemble(
            instruction="""Synthesize the three analyses into a single coherent mathematical model.
            Combine:
            - Entities and their groupings from entity_extraction
            - Numerical mappings and operations from quantity_mapping  
            - Constraints and boundaries from constraint_analysis
            Structure the model as:
            1. Variables: Define unknowns (e.g., rats_per_cage = x)
            2. Equations: Based on totals and relationships
            3. Constraints: Domain restrictions (positive integers, etc.)
            4. Solution path: Step-by-step calculation plan
            Resolve any conflicts between analyses by prioritizing numerical consistency with totals.""",
            contexts_list=[entity_extraction, quantity_mapping, constraint_analysis]
        )

        # PHASE 3: INITIAL SOLUTION ATTEMPT
        initial_solution = await self.generate(
            instruction=f"""Using the unified model:
            {unified_model}
            
            Execute the solution path step by step:
            - Show all intermediate calculations
            - Track units at each step
            - Verify dimensional consistency
            - Stop at the final numerical answer
            Present the answer as a single number in a box: \\boxed{{answer}}""",
            context=unified_model
        )

        # PHASE 4: VALIDATION LOOP (max 2 iterations)
        current_solution = initial_solution
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""Validate the solution by backward substitution:
                Given solution: {current_solution}
                And original problem: {self.problem_text}
                
                Plug the answer back into the original scenario:
                - Recalculate all intermediate totals
                - Verify they match stated totals in the problem
                - Check all constraints are satisfied
                - Ensure no entity counts are fractional or negative
                If valid, respond ONLY with "VALID: [answer]".
                If invalid, respond with "INVALID: [specific reason]" and suggest correction.""",
                context=current_solution
            )

            if "VALID:" in validation:
                break
            else:
                # Revise model based on validation feedback
                current_solution = await self.revise(
                    instruction=f"""Revise the solution based on validation feedback:
                    Validation result: {validation}
                    Original model: {unified_model}
                    
                    Correct the mathematical model or calculations:
                    - Fix identified errors
                    - Adjust variable definitions if needed
                    - Recalculate step by step
                    - Maintain unit tracking
                    Output only the revised numerical answer in \\boxed{{}} format.""",
                    context=current_solution
                )
        else:
            # If loop exhausted, use last solution
            pass

        # PHASE 5: FINAL ANSWER EXTRACTION
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the solution.
            The answer must be:
            - A single number (integer or decimal)
            - No units, no text, no explanation
            - If multiple numbers appear, select the one that solves the main question
            - Use regex to find the number inside \\boxed{{}} if present
            - If no boxed answer, find the last computed number
            Output nothing but the number.""",
            context=current_solution
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer)
        return cleaned if cleaned else "0"