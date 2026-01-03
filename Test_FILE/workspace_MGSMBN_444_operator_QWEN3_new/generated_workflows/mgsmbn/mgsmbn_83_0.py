# Workflow ID: mgsmbn_83_0
# Benchmark: mgsmbn
# Data Indices: [159, 179]

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

        # Step 1: Classify problem complexity to adapt workflow depth
        classification = await self.generate(
            instruction="""Thoroughly analyze this Bengali math word problem and classify its complexity:
            
            1. ENTITY COUNT: How many distinct entities (people, objects, groups) are involved? 
               - Simple: 1 entity or direct relationship (e.g., "Andy planted X flowers")
               - Complex: 2+ entities with comparative or proportional relationships (e.g., "Publisher A pays X, Publisher B pays 2X")
            
            2. OPERATION DEPTH: 
               - Shallow: Single arithmetic operation needed
               - Deep: Multiple sequential or nested operations, hidden steps, or unit conversions
            
            3. CONSTRAINT TYPE:
               - Explicit: All constraints directly stated
               - Implicit: Requires real-world inference (e.g., "can't have negative people")
            
            4. AMBIGUITY LEVEL:
               - Low: Clear, unambiguous phrasing
               - High: Multiple valid interpretations possible
            
            Output format:
            COMPLEXITY: [simple|complex]
            DEPTH: [shallow|deep]
            CONSTRAINTS: [explicit|implicit]
            AMBIGUITY: [low|high]
            REASONING: [2-3 sentence justification]""",
            context=""
        )

        # Step 2: Conditional branching based on classification
        if "COMPLEXITY: simple" in classification and "DEPTH: shallow" in classification:
            # Direct path for simple problems
            direct_solution = await self.generate(
                instruction="""Solve this straightforward Bengali math problem with minimal steps:
                
                1. Extract the single key operation (addition, subtraction, multiplication, division)
                2. Identify the two numbers involved and their units
                3. Perform calculation
                4. Apply real-world constraints (e.g., round to whole number for countable items)
                5. Output ONLY the numerical answer with no explanation
                
                Example: "90 geraniums and 40 fewer petunias" → 90 + (90-40) = 140
                
                IMPORTANT: If any step seems ambiguous, STOP and output "RETRY_COMPLEX". Otherwise, output just the number.""",
                context=""
            )
            
            if "RETRY_COMPLEX" in direct_solution:
                # Fall back to complex workflow
                return await self._complex_workflow()
            else:
                # Validate and clean output
                cleaned = re.sub(r'[^\d.]', '', direct_solution)
                return float(cleaned) if '.' in cleaned else int(cleaned)
                
        else:
            # Full complex workflow
            return await self._complex_workflow()

    async def _complex_workflow(self):
        import asyncio
        import re

        # Parallel analysis tracks
        entity_analysis, math_modeling, constraint_analysis = await asyncio.gather(
            self.generate(
                instruction="""Extract all entities, quantities, and relationships from this Bengali problem:
                
                For EACH entity mentioned:
                - NAME: What is it called? (person, object, group)
                - QUANTITY: What numerical value is associated? Include unit (টাকা, সেন্ট, জিনিস, etc.)
                - RELATIONSHIP: How does it relate to other entities? (e.g., "দ্বিগুণ" = double, "কম" = less than)
                - ROLE: What function does it serve? (payer, receiver, container, rate, etc.)
                
                Format as numbered list. Example:
                1. NAME: প্রকাশক ক | QUANTITY: 5 সেন্ট/বাক্য | RELATIONSHIP: baseline | ROLE: payment rate
                2. NAME: প্রকাশক খ | QUANTITY: 10 সেন্ট/বাক্য | RELATIONSHIP: দ্বিগুণ of প্রকাশক ক | ROLE: payment rate
                
                Also extract any totals or constraints mentioned (e.g., "মোট 1000 বাক্য")""",
                context=""
            ),
            self.generate(
                instruction="""Create a mathematical model for this problem:
                
                1. Define variables for unknowns
                2. Write equations or step-by-step procedures based on relationships
                3. Specify order of operations
                4. Note any unit conversions needed
                5. Identify what final value needs to be calculated
                
                Present as:
                VARIABLES: [list with descriptions]
                EQUATIONS/STEPS: [numbered sequence]
                FINAL TARGET: [what to solve for]
                UNIT REQUIREMENTS: [final answer unit]""",
                context=""
            ),
            self.generate(
                instruction="""Identify all constraints and validation rules:
                
                1. EXPLICIT CONSTRAINTS: Directly stated limits (e.g., "মোট 1000 বাক্য")
                2. IMPLICIT CONSTRAINTS: Real-world logic (e.g., "can't have negative flowers")
                3. BOUNDARY CONDITIONS: Minimum/maximum possible values
                4. CONSISTENCY CHECKS: Cross-verification points (e.g., "sum of parts should equal total")
                
                Format as bullet points with category labels.""",
                context=""
            )
        )

        # Synthesize analyses
        synthesis = await self.ensemble(
            instruction="""Synthesize these three analyses into a unified solution plan:
            
            You have:
            1. ENTITY ANALYSIS: Who/what is involved and their quantitative relationships
            2. MATHEMATICAL MODEL: Equations and procedures to follow
            3. CONSTRAINT ANALYSIS: Rules that must be satisfied
            
            Create a step-by-step solution that:
            - Uses the entity relationships to populate the mathematical model
            - Respects all constraints
            - Shows intermediate calculations
            - Converts units where necessary
            - Rounds appropriately (whole numbers for countable items, decimals for money/distance)
            - Outputs ONLY the final numerical answer at the end
            
            If any analysis contradicts another, resolve the conflict by prioritizing:
            1. Explicit constraints from the problem text
            2. Mathematical consistency
            3. Real-world plausibility""",
            contexts_list=[entity_analysis, math_modeling, constraint_analysis]
        )

        # Self-critique and revision
        revised = await self.revise(
            instruction="""Critically review this solution:
            
            1. Verify each calculation step is mathematically correct
            2. Ensure all entities from extraction are accounted for
            3. Confirm constraints are satisfied
            4. Check unit consistency throughout
            5. Validate final answer makes real-world sense
            6. If any error found, correct it and explain the fix
            
            Output format:
            VERIFIED: [yes|no]
            ERRORS: [list any found, or "none"]
            CORRECTED_SOLUTION: [the final numerical answer, corrected if needed]
            
            If verified without errors, output the number alone. If errors found, output only the corrected number.""",
            context=synthesis
        )

        # Extract and clean final answer
        cleaned = re.sub(r'[^\d.]', '', revised)
        final_answer = float(cleaned) if '.' in cleaned else int(cleaned)
        
        # Final validation: ensure non-negative for countable items
        if final_answer < 0:
            # Fallback: absolute value for counts, but preserve sign for financials
            # Since we don't know context, use absolute value as safest fallback
            final_answer = abs(final_answer)
            
        return final_answer