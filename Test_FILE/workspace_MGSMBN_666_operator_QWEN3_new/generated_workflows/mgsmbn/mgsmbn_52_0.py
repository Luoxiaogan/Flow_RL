# Workflow ID: mgsmbn_52_0
# Benchmark: mgsmbn
# Data Indices: [40]

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

        # PHASE 1: PROBLEM CLASSIFICATION & STRATEGY SELECTION
        classification = await self.generate(
            instruction="""Thoroughly classify this Bengali math word problem by analyzing:
            1. Problem Type: Is it sequential, proportional, distribution, comparison, rate-based, or multi-entity?
            2. Required Operations: What mathematical operations are needed? (addition, subtraction, multiplication, division, fractions, percentages, algebra)
            3. Units Involved: What units are used? (টাকা, পাউন্ড, ঘণ্টা, etc.) Are conversions needed?
            4. Complexity Level: How many distinct steps are required? Are there hidden dependencies?
            5. Answer Constraints: Should the answer be integer? Positive? Within a certain range?
            6. Potential Pitfalls: What are common mistakes for this problem type?
            
            Output your classification as a structured JSON with keys: problem_type, operations, units, steps, constraints, pitfalls.""",
            context=""
        )

        # PHASE 2: ENTITY & RELATIONSHIP EXTRACTION (PARALLEL)
        entity_extraction, relationship_extraction = await asyncio.gather(
            self.generate(
                instruction="""Extract all numerical entities and their context:
                - List every number mentioned with its associated object (e.g., "30টি কমিক বই")
                - Note units for each quantity
                - Identify what each number represents (initial amount, rate, target, etc.)
                - Format as bullet points with clear labels""",
                context=""
            ),
            self.generate(
                instruction="""Extract all relationships and constraints:
                - Mathematical relationships between quantities (e.g., "প্রতিটি কমিক বইয়ের ওজন 1/4 পাউন্ড")
                - Temporal or logical dependencies (e.g., "প্রথমে... তারপর...")
                - Implicit constraints (e.g., "can't have negative toys", "must be whole number")
                - Format as clear, labeled statements""",
                context=""
            )
        )

        # PHASE 3: PROBLEM DECOMPOSITION BASED ON CLASSIFICATION
        decomposition = await self.decompose(
            instruction=f"""Decompose this problem into minimal, executable subproblems based on classification:
            Classification: {classification}
            
            Guidelines:
            - Each subproblem should be solvable independently or with specified dependencies
            - Include ALL necessary steps (even "obvious" ones)
            - Specify input requirements and expected output for each
            - Define dependencies between subproblems (e.g., "step2 depends on step1")
            - Ensure units are tracked through each step
            - Include verification steps where appropriate
            
            Output as structured subproblems with id, description, and dependencies.""",
            context=f"Entities: {entity_extraction}\n\nRelationships: {relationship_extraction}"
        )

        # PHASE 4: PARALLEL SUBPROBLEM SOLUTION GENERATION
        solution_attempts = []
        for i, subproblem in enumerate(decomposition):
            attempt = await self.generate(
                instruction=f"""Solve this subproblem:
                {subproblem['description']}
                
                Context from problem classification: {classification}
                Relevant entities: {entity_extraction}
                Relevant relationships: {relationship_extraction}
                
                Requirements:
                - Show your reasoning step by step
                - Track units throughout
                - If calculation is needed, show the mathematical expression
                - Consider edge cases and constraints
                - Format clearly with final answer for this subproblem""",
                context=""
            )
            solution_attempts.append(attempt)

        # PHASE 5: SUBPROBLEM SOLUTION SYNTHESIS & VERIFICATION
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize these subproblem solutions into a complete answer:
            - Check for consistency between subproblem solutions
            - Verify that dependencies are satisfied (e.g., if step2 uses step1's output, ensure it's correct)
            - Identify any contradictions or errors
            - Combine results according to problem requirements
            - Ensure final answer matches expected format and constraints
            - If errors found, explain and suggest corrections
            
            Output the complete solution path with final numerical answer clearly indicated.""",
            contexts_list=solution_attempts
        )

        # PHASE 6: PRECISE COMPUTATION VIA PROGRAMMER
        final_computation = await self.programmer(
            instruction=f"""Generate and execute Python code to compute the final answer:
            Problem Classification: {classification}
            Complete Solution Path: {synthesized_solution}
            
            Requirements:
            - Code must implement the exact mathematical operations described
            - Handle fractions, decimals, and unit conversions precisely
            - Include input validation (e.g., positive numbers, reasonable ranges)
            - Output only the final numerical answer (no text, no units)
            - If multiple answers possible, choose the most reasonable based on context
            - Handle edge cases gracefully (return error if truly unsolvable)""",
            context=synthesized_solution
        )

        # PHASE 7: FINAL VALIDATION & REFINEMENT
        validated_answer = await self.revise(
            instruction=f"""Validate and refine this final answer:
            Computed Answer: {final_computation}
            Original Problem: {self.problem_text}
            Problem Classification: {classification}
            
            Validation Checklist:
            1. Does the answer make sense in context? (e.g., not negative when impossible)
            2. Does it match the expected format? (integer, decimal, etc.)
            3. Is it within reasonable bounds? (e.g., not 1000 toys when problem mentions 30 books)
            4. Does it satisfy all constraints identified earlier?
            5. Is the unit handling correct? (though final answer should be unitless number)
            
            If validation fails, explain why and provide corrected answer.
            If validation passes, output ONLY the numerical answer (no text, no explanation).""",
            context=final_computation
        )

        return validated_answer