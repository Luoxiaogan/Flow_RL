# Workflow ID: mgsmbn_66_0
# Benchmark: mgsmbn
# Data Indices: [42]

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

        # Step 1: Semantic Disambiguation - Resolve linguistic ambiguities
        semantic_analysis = await self.generate(
            instruction="""Perform deep linguistic analysis of the Bengali problem:
            1. Identify all entities (people, animals, objects) and their roles.
            2. Extract every numerical value and its contextual meaning (e.g., '7টি বিড়ালছানা' = 7 kittens adopted).
            3. Map relational phrases (e.g., 'থেকে', 'গুণ', 'অপেক্ষা') to mathematical operations.
            4. Resolve ambiguities by cross-referencing numbers with real-world plausibility.
            5. Flag any unclear references or missing information.
            Output in structured format: Entities, Quantities, Relationships, Ambiguities.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition - Break into subproblems with dependencies
        subproblems = await self.decompose(
            instruction=f"""Using semantic analysis:
            {semantic_analysis}
            
            Decompose the problem into minimal, solvable subproblems:
            - Each subproblem must have a clear mathematical objective.
            - Explicitly state dependencies (e.g., 'Subproblem 2 requires result from Subproblem 1').
            - Assign unique IDs (e.g., SP1, SP2).
            - For proportional relationships, isolate the base quantity and multiplier.
            - For sequential events, order by chronology.
            Output as list of dicts with keys: id, description, dependencies.""",
            context=semantic_analysis
        )

        # Step 3: Adaptive Strategy Selection
        if len(subproblems) == 1 and "simple arithmetic" in semantic_analysis.lower():
            # Direct solve for trivial cases
            solution_attempt = await self.programmer(
                instruction=f"""Solve directly using Python:
                Problem context: {semantic_analysis}
                Subproblem: {subproblems[0]['description']}
                - Track units explicitly.
                - Convert all quantities to common units before calculation.
                - Round only if context implies integer constraint (e.g., count of animals).
                - Output only the final numerical value.""",
                context=semantic_analysis,
                max_retries=3
            )
            candidate_solutions = [solution_attempt]
        else:
            # Parallel solution generation for complex cases
            solution_tasks = []
            for sp in subproblems:
                # Strategy 1: Programmer-based precise calculation
                task1 = self.programmer(
                    instruction=f"""Solve subproblem with code:
                    {sp['description']}
                    Dependencies: {sp.get('dependencies', 'None')}
                    Semantic context: {semantic_analysis}
                    - Use symbolic unit tracking.
                    - Validate intermediate results against real-world constraints.
                    - Output final value for this subproblem.""",
                    context=semantic_analysis,
                    max_retries=3
                )
                
                # Strategy 2: Generate-based logical reasoning
                task2 = self.generate(
                    instruction=f"""Solve subproblem through reasoning:
                    {sp['description']}
                    Use step-by-step narrative:
                    1. Restate the subproblem in simple terms.
                    2. Identify knowns and unknowns.
                    3. Apply mathematical relationships.
                    4. Derive the answer with justification.
                    Format: 'Answer: [number]'""",
                    context=semantic_analysis
                )
                solution_tasks.extend([task1, task2])
            
            # Execute all solution attempts in parallel
            raw_solutions = await asyncio.gather(*solution_tasks)
            
            # Extract numerical answers from all attempts
            extraction_tasks = []
            for sol in raw_solutions:
                task = self.generate(
                    instruction="""Extract the final numerical answer from the following solution attempt. 
                    Ignore explanations, units, and intermediate steps. 
                    If no clear number is found, return 'ERROR'.
                    Format: ONLY the number (integer or decimal), nothing else.""",
                    context=sol
                )
                extraction_tasks.append(task)
            
            candidate_solutions = await asyncio.gather(*extraction_tasks)

        # Step 4: Ensemble Synthesis with Cross-Validation
        final_answer = await self.ensemble(
            instruction="""Synthesize the candidate solutions:
            1. Compare all numerical answers.
            2. If all agree, return the consensus value.
            3. If disagreement exists:
               a. Identify which subproblem caused divergence.
               b. Re-analyze that subproblem with stricter constraints.
               c. Return the most plausible answer based on semantic context.
            4. Ensure the answer is non-negative and matches real-world constraints (e.g., integer for counts).
            Output ONLY the final numerical value, nothing else.""",
            contexts_list=candidate_solutions
        )

        # Step 5: Final Validation and Formatting
        validated_answer = await self.revise(
            instruction=f"""Validate and format the final answer:
            Proposed answer: {final_answer}
            Original problem: {self.problem_text}
            Semantic analysis: {semantic_analysis}
            
            Checks:
            1. Does the answer violate any real-world constraints? (e.g., negative kittens, fractional people)
            2. Does it match the expected unit/context? (e.g., 'টাকা' implies decimal, 'জিনিস' implies integer)
            3. Is it consistent with all subproblem dependencies?
            
            If valid: Return ONLY the numerical value.
            If invalid: Recalculate using corrected assumptions and return the fixed value.""",
            context=final_answer
        )

        # Extract clean numerical value (remove any residual text)
        clean_answer = await self.generate(
            instruction="""Extract ONLY the numerical value from the following text. 
            Remove any units, explanations, or formatting. 
            If the value is an integer, output without decimal. 
            If decimal, preserve exact precision.
            Example inputs: 'Answer: 40', '40.0টাকা', 'Result: 40.5' → Outputs: '40', '40.0', '40.5'""",
            context=validated_answer
        )

        return clean_answer.strip()