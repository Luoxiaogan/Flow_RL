# Workflow ID: mgsmbn_6_0
# Benchmark: mgsmbn
# Data Indices: [76]

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
        # Generate three independent interpretations of the problem structure
        decomposition_tasks = [
            self.generate(
                instruction="""Perform deep semantic decomposition of the Bengali word problem. Identify:
                1. All entities (people, objects, containers)
                2. All numerical values and their associated units
                3. All actions or transformations (e.g., 'becomes half', 'used to make')
                4. The explicit question being asked
                5. Any implicit constraints (e.g., discrete items, non-negative quantities)
                Format as a structured JSON-like outline with clear labels.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the problem from a mathematical modeling perspective. Specifically:
                - Map the narrative to mathematical operations (ratios, proportions, scaling factors)
                - Identify input-output relationships
                - Flag any ambiguous phrases that could have multiple interpretations
                - Propose the most likely mathematical interpretation with justification
                Structure your response as: [Model Hypothesis] -> [Supporting Evidence] -> [Potential Ambiguities]""",
                context=""
            ),
            self.generate(
                instruction="""Focus exclusively on unit analysis and dimensional consistency:
                - List all units mentioned (ounces, tomatoes, cans, etc.)
                - Trace how units transform through each described operation
                - Identify any unit conversion requirements
                - Verify that the final answer's unit matches the question's requirement
                Present as a unit flowchart in text form: Input Unit -> Operation -> Output Unit""",
                context=""
            )
        ]
        
        decompositions = await asyncio.gather(*decomposition_tasks)

        # PHASE 2: SPECIALIZED SOLUTION GENERATION (PARALLEL)
        # Each decomposition spawns a tailored solution attempt
        solution_tasks = []
        for i, decomp in enumerate(decompositions):
            solution_tasks.append(
                self.generate(
                    instruction=f"""Using this analytical perspective:
                    {decomp}
                    
                    Now generate a complete, step-by-step mathematical solution:
                    - Show all calculations explicitly
                    - Justify each step with reference to the problem text
                    - Handle unit conversions methodically
                    - Verify intermediate results make real-world sense
                    - Box the final numerical answer at the end
                    
                    If you encounter ambiguity, state your assumption clearly.
                    Prioritize solutions that maintain integer quantities for discrete objects.""",
                    context=decomp
                )
            )
        
        raw_solutions = await asyncio.gather(*solution_tasks)

        # PHASE 3: CONSTRAINT-AWARE REVISION (PARALLEL)
        # Each solution is revised with strict validation criteria
        revision_tasks = []
        for sol in raw_solutions:
            revision_tasks.append(
                self.revise(
                    instruction="""Critically revise this solution with the following checklist:
                    1. UNIT CONSISTENCY: Are all units properly tracked and converted?
                    2. REAL-WORLD VALIDITY: Are quantities non-negative? Are discrete items whole numbers?
                    3. STEP VALIDITY: Does each mathematical step follow logically from the problem description?
                    4. AMBIGUITY RESOLUTION: Are any assumptions explicitly stated and justified?
                    5. FINAL ANSWER: Is it a single numerical value as required?
                    
                    If any issue is found, correct it and explain the correction.
                    If the solution is invalid, reconstruct it from scratch using only unambiguous information.
                    Preserve the step-by-step format but enhance rigor and clarity.""",
                    context=sol
                )
            )
        
        refined_solutions = await asyncio.gather(*revision_tasks)

        # PHASE 4: ENSEMBLE SYNTHESIS WITH META-REASONING
        # Synthesize the best answer through comparative analysis
        final_answer = await self.ensemble(
            instruction="""You are given multiple solution attempts for a Bengali math word problem.
            Your task is NOT to average or vote, but to perform meta-reasoning:
            
            1. Compare the logical coherence of each solution's reasoning chain
            2. Evaluate which solution best handles ambiguities with justified assumptions
            3. Verify which solution maintains dimensional consistency throughout
            4. Check which solution respects real-world constraints (discrete items, non-negative quantities)
            5. Identify any consensus among solutions on key steps or final answer
            
            Then, construct the optimal solution by:
            - Adopting the most rigorous reasoning steps
            - Resolving contradictions through first principles
            - Ensuring the final answer is a single numerical value
            - Preserving only the essential calculation steps (no prose)
            
            Output ONLY the final numerical answer as a single integer or decimal.
            No explanations, no units, no formatting — just the number.""",
            contexts_list=refined_solutions
        )

        # PHASE 5: FINAL EXTRACTION AND SANITIZATION
        # Ensure output is clean numerical value
        sanitized = await self.summarize(
            instruction="""Extract ONLY the numerical answer from the following text.
            Remove any units, explanations, or formatting.
            If multiple numbers are present, select the one that is the final answer.
            If no clear number is found, return '0' as fallback.
            Output must be a single integer or decimal number.""",
            context=final_answer
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        clean_answer = re.sub(r'[^\d.]', '', sanitized.strip())
        
        # Handle edge case: if empty, return 0
        if not clean_answer:
            return "0"
            
        # Ensure proper decimal handling
        try:
            # Convert to float then back to string to normalize
            num = float(clean_answer)
            # If integer, return as int string, else as float string
            if num.is_integer():
                return str(int(num))
            else:
                return str(num)
        except:
            return "0"