# Workflow ID: drop_161_0
# Benchmark: drop
# Data Indices: [358, 316]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.llm)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        
        # Step 1: Extract entities and relationships
        structured_context = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        
        # Step 2: Classify the problem type
        problem_type = await self.generate(
            instruction=f"""Classify the problem based on the question and structured context:
            Structured Context: {structured_context}
            
            Categories:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (which is greater, which came first, etc.)
            - Span Extraction (who did, what was the name of, etc.)
            - Multi-step (requires chaining multiple operations)
            
            Provide a concise classification and justification.""",
            context=structured_context
        )
        
        # Step 3: Generate candidate solutions in parallel
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using direct computation:
                Structured Context: {structured_context}
                Problem Type: {problem_type}
                
                Perform the required operations carefully and show all steps.""",
                context=structured_context
            ),
            self.generate(
                instruction=f"""Solve the problem using an alternative approach:
                Structured Context: {structured_context}
                Problem Type: {problem_type}
                
                If arithmetic, provide an estimation. If span extraction, validate against the passage.""",
                context=structured_context
            )
        )
        
        # Step 4: Ensemble decision-making
        final_solution = await self.ensemble(
            instruction=f"""Select or synthesize the best solution from the candidates:
            Candidates:
            1. {candidates[0]}
            2. {candidates[1]}
            
            Criteria:
            - Accuracy
            - Relevance to the question
            - Exact match for span extraction
            - Logical consistency for multi-step problems""",
            contexts_list=candidates
        )
        
        # Step 5: Iterative refinement
        refined_solution = final_solution
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction=f"""Validate the solution:
                Solution: {refined_solution}
                
                Check for:
                - Errors in arithmetic
                - Ambiguities in span extraction
                - Logical inconsistencies""",
                context=refined_solution
            )
            if "error" in validation.lower() or "ambiguity" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Revise the solution based on validation feedback:
                    Feedback: {validation}""",
                    context=refined_solution
                )
            else:
                break
        
        return refined_solution