# Workflow ID: mgsmbn_0_0
# Benchmark: mgsmbn
# Data Indices: [6, 177]

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

        # PHASE 1: SEMANTIC DECOMPOSITION
        # Break problem into structured subproblems with dependencies
        decomposition = await self.decompose(
            instruction="""Perform hierarchical semantic decomposition of this Bengali math word problem.
            Identify:
            1. All numerical entities and what they represent (with units if specified)
            2. All mathematical operations implied by the text (addition, subtraction, multiplication, division, percentage, etc.)
            3. Temporal or logical sequence of operations (what happens first, second, etc.)
            4. Dependencies between values (e.g., "three times more than X" depends on X)
            5. Final unknown to solve for
            6. Any constraints (integer-only, non-negative, etc.)
            
            Structure output as list of subproblems with clear dependencies.
            Each subproblem should be solvable independently once its dependencies are resolved.
            Prioritize chronological/logical order of operations.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY CLASSIFICATION
        # Generate multiple perspectives on problem type and solution approach
        strategy_tasks = [
            self.generate(
                instruction="""Classify this problem as one of: Sequential Operations, Rate Problem, Proportional Reasoning, 
                Distribution Problem, Comparison Problem, or Multi-entity Tracking.
                Then propose the most appropriate solution strategy:
                - For rates: identify rate × quantity = total
                - For proportions: identify base value and percentage/fraction
                - For sequences: identify step-by-step operations in order
                - For distributions: identify total and division logic
                - For comparisons: identify difference calculation
                - For multi-entity: track each entity separately then combine
                
                Also specify what intermediate values need to be calculated before final answer.
                Be explicit about operation order and any unit conversions needed.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from a mathematical modeling perspective.
                Identify:
                1. Variables and their relationships (equations or inequalities)
                2. Known values and unknowns
                3. Whether algebraic solving is needed (solve for x)
                4. Whether iterative calculation is needed
                5. Potential pitfalls or ambiguous interpretations
                
                Propose a step-by-step mathematical model that could solve this problem.
                Format as numbered steps with clear inputs and outputs for each step.""",
                context=""
            ),
            self.generate(
                instruction="""Interpret this problem as a real-world scenario.
                Describe the story in simple terms, then map it to mathematical operations.
                Identify:
                1. What actually happens in the story (chronological events)
                2. What quantities change and how
                3. What the final question is really asking
                4. Any real-world constraints that affect the math (e.g., can't have negative people)
                
                Then translate this narrative into a computational plan.
                Focus on making the math feel intuitive and grounded in the story.""",
                context=""
            )
        ]
        
        strategy_analyses = await asyncio.gather(*strategy_tasks)
        
        # Synthesize best strategy
        selected_strategy = await self.ensemble(
            instruction="""Synthesize the most robust solution strategy from the provided analyses.
            Consider:
            1. Which approach most accurately captures the problem's structure?
            2. Which has the clearest step-by-step plan?
            3. Which best handles potential ambiguities?
            4. Which aligns with the decomposition's dependency graph?
            
            Output a unified strategy that combines the strengths of all analyses.
            Format as clear, numbered steps that can be directly translated to code.
            Include explicit mention of any unit handling or constraint checking needed.""",
            contexts_list=strategy_analyses
        )

        # PHASE 3: GUIDED CODE GENERATION
        # Generate executable code based on decomposition and selected strategy
        code_result = await self.programmer(
            instruction=f"""Generate Python code to solve this Bengali math word problem based on the following:
            
            Problem Decomposition:
            {json.dumps(decomposition, indent=2, ensure_ascii=False)}
            
            Selected Strategy:
            {selected_strategy}
            
            Requirements:
            1. Code must follow the step-by-step plan in the strategy
            2. Handle all dependencies in correct order
            3. Include comments explaining each step in English
            4. Validate intermediate results against constraints (non-negative, integer if required)
            5. Print ONLY the final numerical answer (no text, no units)
            6. Use precise arithmetic (avoid floating point errors when possible)
            7. If percentage calculations are involved, be explicit about increase/decrease direction
            
            Example structure:
            # Step 1: Calculate X based on given value Y
            x = y * 3
            # Step 2: Apply 30% decrease
            x = x * 0.7
            # Step 3: Sum all values for final answer
            final_answer = x + y + z
            print(final_answer)""",
            context=f"Decomposition: {decomposition}

Strategy: {selected_strategy}"
        )

        # Extract numerical answer from code output
        # (Assuming programmer returns code + output, we need the last line of output)
        final_answer = ""
        try:
            # Look for the last line that contains a number
            lines = code_result.strip().split('\n')
            for line in reversed(lines):
                if any(c.isdigit() for c in line):
                    # Extract first number from the line
                    import re
                    numbers = re.findall(r'-?\d+\.?\d*', line)
                    if numbers:
                        final_answer = numbers[0]
                        break
        except:
            # Fallback: return raw code result if parsing fails
            final_answer = code_result

        # PHASE 4: VERIFICATION LOOP
        # Verify that the answer makes sense in context
        verification = await self.generate(
            instruction=f"""Verify the answer {final_answer} against the original problem.
            Reconstruct the problem narrative using this answer:
            1. Does the answer logically follow from the given information?
            2. Do all intermediate steps make sense in the context?
            3. Are there any unit mismatches or constraint violations?
            4. Is the magnitude reasonable? (e.g., not negative when impossible, not extremely large)
            
            If any issues are found, explain what's wrong and suggest correction.
            If no issues, output "VERIFIED: Answer is consistent with problem context."""",
            context=code_result
        )

        if "VERIFIED" not in verification and "consistent" not in verification.lower():
            # If verification fails, revise and try again
            revised_strategy = await self.revise(
                instruction=f"""The following answer failed verification:
                Answer: {final_answer}
                Verification feedback: {verification}
                
                Revise the solution strategy to address these issues.
                Consider alternative interpretations of ambiguous phrases.
                Ensure all steps are mathematically sound and contextually appropriate.
                Output revised step-by-step strategy.""",
                context=selected_strategy
            )
            
            # Regenerate code with revised strategy
            code_result = await self.programmer(
                instruction=f"""Generate Python code based on revised strategy:
                {revised_strategy}
                
                Same requirements as before: precise, commented, prints only final number.""",
                context=revised_strategy
            )
            
            # Extract answer again
            try:
                lines = code_result.strip().split('\n')
                for line in reversed(lines):
                    if any(c.isdigit() for c in line):
                        import re
                        numbers = re.findall(r'-?\d+\.?\d*', line)
                        if numbers:
                            final_answer = numbers[0]
                            break
            except:
                final_answer = code_result

        return final_answer