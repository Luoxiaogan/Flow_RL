# Workflow ID: humaneval_13_0
# Benchmark: humaneval
# Data Indices: [127, 24]

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

        # Step 1: Classify problem type and extract key constraints
        classification = await self.generate(
            instruction="""Analyze this code generation problem and classify it:
            1. Problem Type: Is it mathematical, logical, string manipulation, or algorithmic?
            2. Key Constraints: What are the explicit and implicit constraints from the docstring?
            3. Edge Cases: What edge cases are suggested by the examples or problem description?
            4. Return Type: What exact return type is required (int, float, string, etc.)?
            5. Function Name: Extract the exact function name from ENTRY POINT section.
            
            Format your response as a structured JSON-like analysis with clear sections.""",
            context=""
        )

        # Step 2: Parallel analysis from multiple perspectives
        example_analysis, constraint_analysis, edge_case_analysis = await asyncio.gather(
            self.generate(
                instruction=f"""Analyze the examples in the docstring:
                - What patterns do the input-output pairs reveal?
                - What transformations are being applied?
                - Can you derive a general formula or algorithm from these examples?
                - How do the examples handle edge cases?
                
                Base your analysis on this classification: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Formalize the problem constraints mathematically/logically:
                - Express the problem requirements as formal conditions or equations
                - Identify invariants that must hold true
                - What are the boundary conditions?
                - How would you verify a solution is correct?
                
                Use this classification: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate potential edge cases not shown in examples:
                - Systematically vary inputs along all dimensions mentioned in spec
                - Consider minimum/maximum values, zero cases, negative numbers, empty inputs
                - What inputs would break a naive implementation?
                - How should these edge cases be handled?
                
                Guided by: {classification}""",
                context=""
            )
        )

        # Step 3: Generate multiple candidate solutions
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution based primarily on example patterns:
                - Implement the most straightforward interpretation of the examples
                - Focus on reproducing the exact behavior shown
                - Keep code simple and direct
                - Ensure function name matches ENTRY POINT exactly
                
                Example analysis: {example_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution based on formal constraints:
                - Implement the mathematically/logically rigorous solution
                - Handle all edge cases identified in constraint analysis
                - Prioritize correctness over simplicity
                - Ensure function name matches ENTRY POINT exactly
                
                Constraint analysis: {constraint_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution focused on edge case handling:
                - Design specifically to handle the edge cases identified
                - Include explicit checks for boundary conditions
                - May be more verbose but maximally robust
                - Ensure function name matches ENTRY POINT exactly
                
                Edge cases: {edge_case_analysis}""",
                context=""
            )
        )

        # Step 4: Ensemble to select or synthesize best solution
        synthesized = await self.ensemble(
            instruction="""Select the best solution or synthesize a hybrid:
            - Prioritize solutions that handle edge cases correctly
            - Favor mathematical rigor over example extrapolation when they conflict
            - Ensure the function name matches ENTRY POINT exactly
            - Verify return types match examples precisely
            - If solutions can be combined, create a superior hybrid
            - Output ONLY the final code, no explanations""",
            contexts_list=candidates
        )

        # Step 5: Targeted revision for interface compliance
        interface_checked = await self.revise(
            instruction=f"""Critically review this code for interface compliance:
            1. Does the function name EXACTLY match the ENTRY POINT? (Case-sensitive)
            2. Do return types match the examples precisely? (int vs float, string literals)
            3. Are all edge cases from our analysis handled?
            4. Is the code free of over-engineering? (Implement only what's specified)
            
            If any issues are found, revise the code to fix them. Output ONLY the corrected code.
            
            Classification context: {classification}""",
            context=synthesized
        )

        # Step 6: Final validation through example simulation
        final = await self.revise(
            instruction=f"""Simulate the provided examples mentally:
            - Walk through each example step by step
            - Verify the code produces exactly the expected output
            - Check for off-by-one errors, type mismatches, or logical flaws
            - If any discrepancy is found, fix the code immediately
            
            Output ONLY the final, validated code. No explanations or markdown.
            
            Example analysis: {example_analysis}
            Edge cases: {edge_case_analysis}""",
            context=interface_checked
        )

        return final