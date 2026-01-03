# Workflow ID: mgsmbn_54_0
# Benchmark: mgsmbn
# Data Indices: [108]

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
        """
        Universal workflow for MGSM Bengali math word problems.
        Combines parallel analysis, conditional routing, and iterative refinement.
        """
        import asyncio
        import re
        
        # PHASE 1: PARALLEL ANALYSIS - Extract linguistic and mathematical features
        linguistic_analysis, math_classification = await asyncio.gather(
            self.generate(
                instruction="""Thoroughly analyze the Bengali text to extract:
                1. All named entities (people, days, objects)
                2. All numerical values with their units (টাকা, মাইল, ঘণ্টা, etc.)
                3. Action verbs and their sequence (হেঁটেছিলেন, কিনেছে, ভাগ করেছে)
                4. Relationships between quantities (বেশি, কম, গুণ, ভাগ)
                5. Explicit constraints and conditions
                Format as structured JSON with keys: entities, quantities, actions, relationships, constraints""",
                context=""
            ),
            self.generate(
                instruction="""Classify this math problem by type and complexity:
                1. Primary category: Sequential, Rate, Proportional, Distribution, Comparison, Multi-entity
                2. Required operations: Addition, Subtraction, Multiplication, Division, Fractions, Percentages, Algebra
                3. Complexity level: Simple (1-2 steps), Medium (3-4 steps), Complex (5+ steps or hidden steps)
                4. Potential pitfalls: Unit conversion, Hidden steps, Contextual constraints, Multiple interpretations
                5. Recommended solution strategy: Direct computation, Step-by-step reasoning, Algebraic approach
                Provide detailed classification with justification for each assessment.""",
                context=""
            )
        )
        
        # PHASE 2: SOLUTION ROADMAP - Synthesize analysis into executable plan
        solution_roadmap = await self.ensemble(
            instruction="""Create a comprehensive solution roadmap by synthesizing:
            1. Linguistic analysis: What entities and quantities are involved?
            2. Mathematical classification: What type of problem is this?
            3. Generate a step-by-step plan that includes:
               - Required mathematical operations in sequence
               - Inputs and outputs for each step
               - Unit handling requirements
               - Verification steps to ensure answer makes sense
               - Alternative approaches if primary method fails
            4. Identify any ambiguous elements that need clarification
            5. Specify confidence level in the roadmap (High/Medium/Low)
            Format as numbered steps with clear dependencies between steps.""",
            contexts_list=[linguistic_analysis, math_classification]
        )
        
        # PHASE 3: CONDITIONAL ROUTING - Choose solution strategy based on complexity
        if "Simple" in math_classification or "Direct computation" in math_classification:
            # Route to programmer for straightforward calculations
            solution_attempt = await self.programmer(
                instruction=f"""Generate and execute Python code to solve this problem:
                Solution Roadmap: {solution_roadmap}
                
                Requirements:
                1. Use exact arithmetic (no floating point errors)
                2. Handle units appropriately (convert if necessary)
                3. Include verification step to check answer against problem constraints
                4. Return only the final numerical answer
                5. If multiple answers possible, return most contextually appropriate
                
                Code should be self-contained and handle edge cases.""",
                context=solution_roadmap
            )
        else:
            # Use generate-revise loop for complex problems
            initial_solution = await self.generate(
                instruction=f"""Solve this problem step by step following the roadmap:
                Roadmap: {solution_roadmap}
                
                Requirements:
                1. Show all intermediate calculations
                2. Explain reasoning for each step
                3. Handle units consistently
                4. Check for contextual constraints (no negative items, fractional people, etc.)
                5. Present final answer clearly at the end
                6. Include verification that answer satisfies all problem conditions""",
                context=solution_roadmap
            )
            
            # Refine and verify the solution
            solution_attempt = await self.revise(
                instruction="""Critically review this solution:
                1. Verify all calculations are correct
                2. Check unit consistency throughout
                3. Ensure answer satisfies all problem constraints
                4. Confirm no steps were missed
                5. Validate that answer makes sense in real-world context
                6. Improve clarity and precision of explanation
                7. Extract final numerical answer and present it prominently
                
                If any issues found, correct them and explain the correction.""",
                context=initial_solution
            )
        
        # PHASE 4: TOURNAMENT VERIFICATION - Generate alternative solutions for complex problems
        if "Complex" in math_classification or "Low" in solution_roadmap:
            # Generate multiple solution approaches
            alternative_solutions = await asyncio.gather(
                self.generate(
                    instruction=f"""Solve using algebraic approach:
                    Roadmap: {solution_roadmap}
                    Focus on setting up equations and solving systematically.""",
                    context=solution_roadmap
                ),
                self.generate(
                    instruction=f"""Solve using proportional reasoning:
                    Roadmap: {solution_roadmap}
                    Focus on ratios, percentages, and scaling relationships.""",
                    context=solution_roadmap
                ),
                self.generate(
                    instruction=f"""Solve using step-by-step arithmetic:
                    Roadmap: {solution_roadmap}
                    Focus on sequential operations without algebra.""",
                    context=solution_roadmap
                )
            )
            
            # Ensemble to select best solution
            solution_attempt = await self.ensemble(
                instruction="""Evaluate these three solution approaches:
                1. Algebraic approach
                2. Proportional reasoning approach  
                3. Step-by-step arithmetic approach
                
                Select the most reliable solution based on:
                - Mathematical correctness
                - Consistency with problem constraints
                - Clarity of reasoning
                - Real-world plausibility
                - Handling of edge cases
                
                Extract the final numerical answer from the selected solution.
                If answers differ, analyze why and select the most defensible answer.""",
                contexts_list=[solution_attempt] + alternative_solutions
            )
        
        # PHASE 5: FINAL VERIFICATION - Work backwards to validate answer
        final_verification = await self.generate(
            instruction=f"""Perform final verification:
            1. Extract the numerical answer from: {solution_attempt}
            2. Work backwards through the problem to verify this answer satisfies all conditions
            3. Check for any remaining inconsistencies or violations of constraints
            4. If answer is invalid, explain why and provide corrected answer
            5. If answer is valid, confirm with "VERIFIED: [answer]"
            
            Return only the final verified numerical answer, or corrected answer if needed.""",
            context=solution_attempt
        )
        
        # Extract final numerical answer using regex to handle various formats
        import re
        # Look for patterns like "VERIFIED: 13", "Answer: 13", or just "13"
        match = re.search(r'(?:VERIFIED|Answer|Final answer|উত্তর)[:\s]*([0-9]+\.?[0-9]*)', final_verification)
        if match:
            final_answer = match.group(1)
        else:
            # Fallback: extract any number from the text
            numbers = re.findall(r'[0-9]+\.?[0-9]*', final_verification)
            final_answer = numbers[0] if numbers else "0"
        
        return final_answer