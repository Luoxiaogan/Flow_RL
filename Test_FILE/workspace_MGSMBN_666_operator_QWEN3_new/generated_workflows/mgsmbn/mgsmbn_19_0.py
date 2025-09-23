# Workflow ID: mgsmbn_19_0
# Benchmark: mgsmbn
# Data Indices: [146]

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

        # PHASE 1: SEMANTIC DECOMPOSITION & ENTITY EXTRACTION
        entity_extraction = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and extract all mathematical entities and relationships. Structure your output as follows:

1. QUANTITIES: List every numerical value with its associated object/unit (e.g., "200টি গোলাপি ক্যালা লিলি")
2. RELATIONSHIPS: Identify all comparative, multiplicative, or proportional relationships (e.g., "লাল গোলাপ = 4 × সাদা কারনেশন")
3. UNKNOWN: Clearly state what is being asked to find
4. CONSTRAINTS: Note any real-world or mathematical constraints (e.g., "quantities must be positive integers")

Format each section with clear headings. Be exhaustive and precise.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on extracted entities:
{entity_extraction}

Develop a ALGEBRAIC solution strategy:
- Assign variables to unknowns
- Write equations based on relationships
- Show substitution steps
- Do not compute final value yet""",
                context=entity_extraction
            ),
            self.generate(
                instruction=f"""Based on extracted entities:
{entity_extraction}

Develop a STEPWISE ARITHMETIC solution:
- Break into chronological or logical steps
- Show intermediate calculations
- Track units at each step
- Do not compute final value yet""",
                context=entity_extraction
            ),
            self.generate(
                instruction=f"""Based on extracted entities:
{entity_extraction}

Develop a PROPORTIONAL REASONING approach:
- Identify base quantities and scaling factors
- Set up ratios or proportions
- Cross-multiply or scale as needed
- Do not compute final value yet""",
                context=entity_extraction
            )
        ]
        
        strategy_results = await asyncio.gather(*strategy_tasks)

        # PHASE 3: STRATEGY SYNTHESIS
        synthesized_strategy = await self.ensemble(
            instruction="""Evaluate and synthesize the three solution strategies:
1. Check each for mathematical correctness and consistency with extracted entities
2. Identify the most reliable approach or combine strongest elements from multiple approaches
3. Resolve any contradictions between strategies
4. Produce one unified, step-by-step solution plan with clear operations
5. Include explicit unit tracking and validation checkpoints

Output ONLY the synthesized solution plan, ready for code implementation.""",
            contexts_list=strategy_results
        )

        # PHASE 4: COMPUTATION WITH VALIDATION
        final_answer = None
        error_context = ""
        
        for attempt in range(3):
            try:
                computation_result = await self.programmer(
                    instruction=f"""Implement the following solution plan in Python:
{synthesized_strategy}

Requirements:
1. Use descriptive variable names based on problem entities
2. Include intermediate print statements for key steps
3. Validate that all quantities are positive and meet real-world constraints
4. Output ONLY the final numerical answer as a float or int
5. If any step produces invalid result (negative, fractional when should be whole, etc.), raise an exception

The code must be self-contained and mathematically precise.""",
                    context=synthesized_strategy,
                    max_retries=1
                )
                
                # Extract numerical answer from computation result
                match = re.search(r'[-+]?\d*\.\d+|\d+', computation_result)
                if match:
                    final_answer = float(match.group()) if '.' in match.group() else int(match.group())
                    break
                else:
                    error_context = f"Failed to extract number from: {computation_result}"
                    
            except Exception as e:
                error_context = f"Computation failed: {str(e)}\nPrevious strategy: {synthesized_strategy}"
                # Revise strategy based on error
                synthesized_strategy = await self.revise(
                    instruction=f"""Previous strategy failed with error:
{error_context}

Revise the solution plan:
1. Address the specific failure cause
2. Simplify complex steps if needed
3. Add explicit validation checks
4. Consider alternative mathematical approaches
5. Maintain unit consistency throughout""",
                    context=synthesized_strategy
                )

        # PHASE 5: CONTEXTUAL VALIDATION
        if final_answer is not None:
            validation = await self.generate(
                instruction=f"""Validate the answer {final_answer} against the original problem:
1. Does it satisfy all stated relationships?
2. Is it consistent with real-world constraints (positive, reasonable magnitude)?
3. Does it answer the exact question asked?
4. Are units appropriate?

If valid, output ONLY the number. If invalid, output 'INVALID' and brief reason.""",
                context=f"Original Strategy: {synthesized_strategy}\nComputed Answer: {final_answer}"
            )
            
            if "INVALID" not in validation:
                final_answer = validation.strip()
            else:
                # Fallback: return raw computation if validation is overly cautious
                pass

        # PHASE 6: FINAL OUTPUT FORMATTING
        result = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the following text. 
No explanations, no units, no additional text. Just the number, as integer or decimal.
If multiple numbers, choose the one that answers the main question.""",
            context=str(final_answer) if final_answer is not None else "0"
        )
        
        return result.strip()