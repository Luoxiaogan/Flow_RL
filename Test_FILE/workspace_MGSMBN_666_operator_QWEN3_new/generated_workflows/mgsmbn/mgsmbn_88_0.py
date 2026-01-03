# Workflow ID: mgsmbn_88_0
# Benchmark: mgsmbn
# Data Indices: [109]

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

        # Step 1: Classify problem complexity to determine depth of processing
        classification = await self.generate(
            instruction="""Analyze this Bengali math word problem and classify its complexity:
            - Is it a single-step or multi-step problem?
            - Does it involve hidden operations (e.g., unit conversion, time scaling)?
            - Are there narrative elements that are irrelevant to calculation?
            - Does it require proportional reasoning, distribution, or comparison?
            - What is the expected output format (integer, decimal, unit)?
            
            Respond in this structured format:
            COMPLEXITY: [simple|moderate|complex]
            STEPS_ESTIMATE: [number of logical steps]
            HIDDEN_OPERATIONS: [yes|no]
            UNITS_INVOLVED: [list of units like টাকা, ঘণ্টা, etc.]
            OUTPUT_TYPE: [integer|decimal]""",
            context=""
        )

        # Step 2: Conditional Branch - Simple vs Complex handling
        if "COMPLEXITY: simple" in classification and "STEPS_ESTIMATE: 1" in classification:
            # Direct path for simple problems
            direct_spec = await self.generate(
                instruction="""Generate a precise Python code specification to solve this problem.
                - Extract all numbers and their meanings
                - Identify the single mathematical operation required
                - Specify variable names and expected output
                - Ensure unit consistency
                - Output ONLY the final numerical answer (no text, no units)
                
                Example specification:
                total = 15 * 4
                result = total
                print(result)""",
                context=classification
            )
            
            result = await self.programmer(
                instruction="Execute the mathematical operation and return only the numerical result.",
                context=direct_spec
            )
            
        else:
            # Full workflow for complex problems
            
            # Step 3: Decompose into subproblems with dependencies
            subproblems = await self.decompose(
                instruction="""Break this problem into sequential subproblems. For each:
                - Clearly state what needs to be calculated
                - Identify inputs and outputs
                - Specify dependencies (which subproblems must be solved first)
                - Note any unit conversions or hidden assumptions
                - Flag any ambiguous phrases needing clarification
                
                Ensure the decomposition follows chronological or logical order.
                Example:
                id: 1
                description: Calculate monthly cost by multiplying frequency by unit cost
                dependencies: 
                
                id: 2
                description: Scale monthly cost to annual by multiplying by 12
                dependencies: 1""",
                context=classification
            )
            
            # Step 4: Parallel linguistic and mathematical interpretation
            linguistic_analysis = await self.generate(
                instruction="""Perform deep linguistic analysis:
                - Identify all entities (people, objects)
                - Extract all numerical values and their contextual meaning
                - Map verbs to mathematical operations (e.g., 'ভাগ করা' → division)
                - Identify temporal/spatial relationships
                - Flag ambiguous phrases that could have multiple interpretations""",
                context=""
            )
            
            mathematical_model = await self.generate(
                instruction="""Create a formal mathematical model:
                - Define variables with units
                - Write equations representing relationships
                - Specify order of operations
                - Include any constraints (e.g., non-negative, integer-only)
                - Note any proportionalities or ratios""",
                context=""
            )
            
            # Step 5: Ensemble merge of interpretations
            merged_spec = await self.ensemble(
                instruction="""Synthesize the linguistic and mathematical analyses into a unified problem specification.
                - Resolve any conflicts between interpretations
                - Create a step-by-step computational plan
                - Ensure all units are consistent and conversions are explicit
                - Format as executable pseudo-code with clear variable names
                - Include validation checks for reasonableness""",
                contexts_list=[linguistic_analysis, mathematical_model]
            )
            
            # Step 6: Generate executable code specification
            code_spec = await self.generate(
                instruction=f"""Based on the merged specification and subproblems, generate Python code that:
                - Solves each subproblem in dependency order
                - Uses descriptive variable names
                - Includes comments explaining each step
                - Validates intermediate results (e.g., no negative quantities)
                - Outputs ONLY the final numerical answer (no text, no units)
                
                Subproblems to solve:
                {subproblems}
                
                Merged specification:
                {merged_spec}""",
                context=f"{subproblems}

{merged_spec}"
            )
            
            # Step 7: Execute and validate
            result = await self.programmer(
                instruction="Execute the code and return only the numerical result.",
                context=code_spec,
                max_retries=3
            )
            
            # Step 8: Validation loop
            for _ in range(2):  # Allow up to 2 revisions
                validation = await self.generate(
                    instruction=f"""Validate this result against the original problem:
                    - Does the number make sense contextually? (e.g., no fractional people)
                    - Are units handled correctly?
                    - Does it match the expected output type (integer/decimal)?
                    - Are all problem constraints satisfied?
                    
                    If valid, respond "VALID". If invalid, explain exactly what's wrong.""",
                    context=f"RESULT: {result}

CLASSIFICATION: {classification}"
                )
                
                if "VALID" in validation:
                    break
                else:
                    # Revise code specification based on validation feedback
                    code_spec = await self.revise(
                        instruction=f"""Fix the issues identified in validation:
                        {validation}
                        
                        Revise the code specification to correct these errors while preserving the correct parts.
                        Ensure output is still ONLY the numerical answer.""",
                        context=code_spec
                    )
                    result = await self.programmer(
                        instruction="Execute the revised code and return only the numerical result.",
                        context=code_spec,
                        max_retries=3
                    )

        # Step 9: Final formatting - ensure pure numerical output
        final_result = await self.revise(
            instruction="""Extract ONLY the numerical answer from the result.
            - Remove any text, units, or explanations
            - Ensure it's a valid number (integer or decimal)
            - If multiple numbers, select the final answer
            - If no number found, return 0
            
            Examples:
            Input: "The answer is 720 dollars" → Output: "720"
            Input: "Result: 45.5" → Output: "45.5"
            Input: "No solution" → Output: "0" """,
            context=result
        )
        
        # Clean extraction using regex as fallback
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", final_result)
        if numbers:
            return numbers[-1]  # Return last number found (likely the final answer)
        else:
            return "0"  # Fallback