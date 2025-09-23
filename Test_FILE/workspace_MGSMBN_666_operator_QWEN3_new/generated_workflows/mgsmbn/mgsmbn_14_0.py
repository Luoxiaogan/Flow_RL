# Workflow ID: mgsmbn_14_0
# Benchmark: mgsmbn
# Data Indices: [36]

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
        import json

        # STEP 1: PARALLEL SEMANTIC EXTRACTION
        # Generate multiple interpretive lenses to avoid early bias
        extraction_tasks = [
            self.generate(
                instruction="""Perform QUANTITY-CENTRIC extraction:
                - Identify all numerical values and what they quantify (e.g., '5 ties', '$40 each')
                - Map comparative phrases ('দ্বিগুণ', '50% বেশি') to mathematical operations
                - List unknowns and what must be calculated
                - Output in structured bullet points""",
                context=""
            ),
            self.generate(
                instruction="""Perform RELATIONSHIP-CENTRIC extraction:
                - Identify all entities (people, objects, categories)
                - Map relationships between entities (e.g., 'red ties are twice blue ties')
                - Identify proportional, comparative, or functional dependencies
                - Output as entity-relationship pairs""",
                context=""
            ),
            self.generate(
                instruction="""Perform GOAL-CENTRIC extraction:
                - What is the final question asking for?
                - What intermediate values must be known to answer it?
                - What constraints or conditions apply?
                - Output as a goal tree with prerequisites""",
                context=""
            )
        ]
        
        extractions = await asyncio.gather(*extraction_tasks)
        
        # STEP 2: ENSEMBLE INTO UNIFIED PROBLEM MODEL
        unified_model = await self.ensemble(
            instruction="""Synthesize these three perspectives into a single coherent problem model:
            - Resolve conflicts between interpretations
            - Preserve all critical numerical relationships
            - Structure as: Knowns, Unknowns, Relationships, Constraints, Solution Goal
            - Format in clear sections with headers""",
            contexts_list=extractions
        )

        # STEP 3: ASSESS COMPLEXITY & CHOOSE PATH
        complexity_analysis = await self.generate(
            instruction=f"""Analyze this problem model:
            {unified_model}
            
            Classify complexity:
            - SIMPLE: Single calculation, no dependencies
            - MODERATE: 2-3 steps, linear dependencies
            - COMPLEX: Multiple entities, branching logic, or iterative calculations
            
            Also determine:
            - Required mathematical operations
            - Potential pitfalls (unit conversions, percentage traps, etc.)
            - Expected answer type (integer, decimal, etc.)""",
            context=unified_model
        )

        # STEP 4A: SIMPLE PROBLEMS - DIRECT SOLUTION
        if "SIMPLE" in complexity_analysis:
            direct_solution = await self.programmer(
                instruction=f"""Solve directly using this model:
                {unified_model}
                
                Write Python code that:
                - Uses only the given values and relationships
                - Performs the necessary calculation
                - Outputs ONLY the numerical answer (no text)
                - Handle units if needed (convert to consistent unit first)""",
                context=unified_model,
                max_retries=3
            )
            # Extract just the number from programmer output
            final_answer = await self.generate(
                instruction="Extract ONLY the numerical answer from this output. No units, no text.",
                context=direct_solution
            )
            return final_answer.strip()

        # STEP 4B: MODERATE/COMPLEX - HIERARCHICAL DECOMPOSITION
        else:
            decomposition = await self.decompose(
                instruction=f"""Break this problem into 2-4 essential computational steps:
                Problem Model:
                {unified_model}
                
                Requirements:
                - Each step must produce a concrete intermediate value
                - Specify dependencies (which steps rely on others)
                - Include the mathematical operation needed
                - Format each step as: [ID]: [Description] | Depends on: [IDs] | Operation: [type]""",
                context=unified_model
            )

            # Validate each subproblem before solving
            solved_values = {}
            for step in decomposition:
                step_id = step['id']
                step_desc = step['description']
                dependencies = step.get('dependencies', '').split(',') if step.get('dependencies') else []
                
                # Wait for dependencies to be solved
                for dep in dependencies:
                    dep = dep.strip()
                    if dep and dep not in solved_values:
                        # This shouldn't happen in topological order, but guard against it
                        continue
                
                # Validate step specification
                validation = await self.generate(
                    instruction=f"""Validate this computational step:
                    Step: {step_desc}
                    Dependencies: {dependencies}
                    Available values: {json.dumps(solved_values)}
                    
                    Check:
                    - Are all required inputs available?
                    - Is the mathematical operation clearly defined?
                    - Does this step logically follow from dependencies?
                    - Will the output be a single numerical value?
                    
                    If valid, respond 'VALID'. If not, explain why.""",
                    context=step_desc
                )
                
                if "VALID" not in validation:
                    # Revise step description if invalid
                    step_desc = await self.revise(
                        instruction=f"""Fix this step based on validation feedback:
                        Validation: {validation}
                        Original: {step_desc}
                        Available values: {json.dumps(solved_values)}
                        
                        Make it computationally precise and self-contained.""",
                        context=step_desc
                    )
                
                # Solve step using Programmer
                step_solution = await self.programmer(
                    instruction=f"""Compute this value:
                    {step_desc}
                    
                    Given these previously computed values:
                    {json.dumps(solved_values)}
                    
                    Write Python code that:
                    - Uses only the specified inputs
                    - Performs the required calculation
                    - Outputs ONLY the numerical result (no text, no units)
                    - Handle any unit conversions internally""",
                    context=step_desc,
                    max_retries=3
                )
                
                # Extract numerical result
                step_result = await self.generate(
                    instruction="Extract ONLY the numerical answer from this output. No text, no units.",
                    context=step_solution
                )
                solved_values[step_id] = step_result.strip()

            # STEP 5: SYNTHESIZE FINAL ANSWER
            final_synthesis = await self.generate(
                instruction=f"""The problem has been solved through these steps:
                {json.dumps(solved_values, indent=2)}
                
                The final answer should be the value that answers the original question.
                Extract and return ONLY that numerical value.""",
                context=json.dumps(solved_values)
            )

            # STEP 6: CONTEXTUAL VALIDATION
            final_validation = await self.generate(
                instruction=f"""Validate this final answer against the original problem:
                Answer: {final_synthesis}
                Original Problem: {self.problem_text}
                
                Check:
                - Does this answer make real-world sense?
                - Are units consistent (if any)?
                - Does it satisfy all stated conditions?
                - Is the magnitude reasonable?
                
                If valid, return the answer unchanged. If invalid, recalculate using correct logic.""",
                context=final_synthesis
            )
            
            return final_validation.strip()