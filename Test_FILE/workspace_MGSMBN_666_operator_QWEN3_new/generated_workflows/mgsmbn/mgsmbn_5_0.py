# Workflow ID: mgsmbn_5_0
# Benchmark: mgsmbn
# Data Indices: [78, 86]

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

        # Step 1: Assess complexity to determine workflow depth
        complexity_assessment = await self.generate(
            instruction="""Analyze the problem and rate its complexity from 1-5 based on:
            - Number of distinct entities (people, objects, units)
            - Number of mathematical operations required
            - Presence of hidden steps or implicit constraints
            - Temporal or conditional dependencies
            Return only the number (1-5).""",
            context=""
        )
        
        try:
            complexity = int(complexity_assessment.strip())
        except:
            complexity = 3  # Default to medium complexity if parsing fails

        # Step 2: Parallel semantic analysis (Diamond Pattern)
        if complexity > 2:
            analysis_tasks = [
                self.generate(
                    instruction="""Extract all entities, actions, and quantities:
                    - List every person, object, or unit mentioned
                    - For each, note associated numbers and relationships
                    - Identify actions (give, receive, calculate, etc.) and their sequence
                    - Format as bullet points with clear labels""",
                    context=""
                ),
                self.generate(
                    instruction="""Identify all mathematical relationships and constraints:
                    - Explicit equations or proportions
                    - Implicit constraints (e.g., non-negative quantities)
                    - Unit consistency requirements
                    - Temporal or logical dependencies
                    - Format as numbered list with explanations""",
                    context=""
                ),
                self.generate(
                    instruction="""Determine the core question and required output:
                    - What is the problem explicitly asking for?
                    - What units or format should the answer have?
                    - What real-world constraints apply (e.g., no fractional people)?
                    - Format as a structured summary""",
                    context=""
                )
            ]
            analyses = await asyncio.gather(*analysis_tasks)
            
            # Synthesize parallel analyses
            synthesized_analysis = await self.ensemble(
                instruction="""Synthesize the three analyses into a unified problem understanding:
                - Resolve any contradictions by prioritizing mathematically explicit information
                - Preserve all critical entities, relationships, and constraints
                - Highlight the exact question being asked and required output format
                - Structure as: Entities | Relationships | Constraints | Question""",
                contexts_list=analyses
            )
        else:
            # Simple problems: direct extraction
            synthesized_analysis = await self.generate(
                instruction="""Directly extract:
                - Key numbers and what they represent
                - Required calculation
                - Answer format
                Format concisely.""",
                context=""
            )

        # Step 3: Decompose into subproblems (if complex)
        if complexity > 2:
            decomposition = await self.decompose(
                instruction="""Break the problem into minimal, ordered subproblems:
                - Each subproblem should be solvable with basic arithmetic or logic
                - Specify dependencies (which subproblems must be solved first)
                - Include variable definitions based on extracted entities
                - Ensure real-world constraints are embedded in each step
                Return as list of dicts with 'id', 'description', 'dependencies'.""",
                context=synthesized_analysis
            )
        else:
            # For simple problems, create a single subproblem
            decomposition = [{
                "id": "step_1",
                "description": "Solve the entire problem in one step",
                "dependencies": ""
            }]

        # Step 4: Solve each subproblem with conditional routing
        subproblem_results = {}
        for subproblem in decomposition:
            sub_id = subproblem["id"]
            description = subproblem["description"]
            
            # Classify subproblem type
            classification = await self.generate(
                instruction=f"""Classify this subproblem: '{description}'
                Categories:
                - COMPUTATIONAL: Requires arithmetic calculation
                - LOGICAL: Requires inference or constraint satisfaction
                - VALIDATION: Requires checking consistency
                Return only the category name in uppercase.""",
                context=synthesized_analysis
            )
            
            max_retries = 3
            for attempt in range(max_retries):
                if "COMPUTATIONAL" in classification.upper():
                    # Use programmer for precise math
                    solution = await self.programmer(
                        instruction=f"""Solve this subproblem with exact computation:
                        Problem: {description}
                        Context: {synthesized_analysis}
                        Define variables clearly. Show calculation steps in code.
                        Return only the final numerical result, no text.""",
                        context=synthesized_analysis,
                        max_retries=1
                    )
                else:
                    # Use generate + revise for logical steps
                    solution = await self.generate(
                        instruction=f"""Solve this subproblem logically:
                        {description}
                        Use the context to ensure consistency.
                        Show reasoning step by step.
                        End with 'Final Answer: [number]'""",
                        context=synthesized_analysis
                    )
                    # Extract number from text
                    solution = await self.generate(
                        instruction="Extract only the final numerical answer from the text. If none found, return 'ERROR'.",
                        context=solution
                    )
                
                # Validate solution
                validation = await self.generate(
                    instruction=f"""Validate this solution for subproblem '{description}':
                    Solution: {solution}
                    Check for:
                    - Negative quantities where impossible
                    - Fractional results for discrete items
                    - Unit mismatches
                    - Consistency with original problem
                    Return 'VALID' if acceptable, otherwise describe issue.""",
                    context=synthesized_analysis
                )
                
                if "VALID" in validation.upper() and "ERROR" not in solution.upper():
                    subproblem_results[sub_id] = solution.strip()
                    break
                else:
                    if attempt < max_retries - 1:
                        # Revise based on validation feedback
                        solution = await self.revise(
                            instruction=f"""Revise the solution based on this feedback:
                            {validation}
                            Ensure the answer is non-negative, integer if required, and unit-consistent.
                            Return only the corrected numerical value.""",
                            context=solution
                        )
                    else:
                        # Final fallback: use generate with stricter constraints
                        solution = await self.generate(
                            instruction=f"""Solve conservatively:
                            {description}
                            Assume discrete quantities, non-negative results.
                            Return only the number.""",
                            context=synthesized_analysis
                        )
                        subproblem_results[sub_id] = solution.strip()

        # Step 5: Combine subproblem results (if multiple)
        if len(subproblem_results) > 1:
            final_calculation_context = "\n".join([f"{k}: {v}" for k, v in subproblem_results.items()])
            final_answer = await self.programmer(
                instruction=f"""Combine subproblem results to get final answer:
                Subproblem Results:
                {final_calculation_context}
                
                Perform any final arithmetic operations needed.
                Return only the numerical result, no text.""",
                context=final_calculation_context
            )
        else:
            final_answer = list(subproblem_results.values())[0]

        # Step 6: Meta-validation (sanity check)
        sanity_check = await self.generate(
            instruction=f"""Re-read the original problem and verify:
            Proposed Answer: {final_answer}
            - Does it satisfy all stated conditions?
            - Is it within plausible real-world bounds?
            - Are units and format correct?
            If valid, return 'CONFIRMED: [answer]'. If not, return 'REJECTED: [reason]'.""",
            context=synthesized_analysis
        )
        
        if "CONFIRMED" in sanity_check.upper():
            final_answer = sanity_check.split(":")[1].strip()
        else:
            # Fallback: return best available answer
            pass

        # Clean and return final numerical answer
        # Extract number from any remaining text
        number_match = re.search(r'[-+]?\d*\.\d+|\d+', str(final_answer))
        if number_match:
            return number_match.group(0)
        else:
            return "0"  # Ultimate fallback