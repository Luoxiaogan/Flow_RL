# Workflow ID: hotpotqa_309_0
# Benchmark: hotpotqa
# Data Indices: [2754, 1432, 3833, 2699, 2998]

<operator id="1" type="agent">
        <instruction>Think step by step to identify the core entity in the question and locate its relevant context.</instruction>
        <input>problem</input>
        <output>core_entity, context_snippet</output>
    </operator>
    
    <operator id="2" type="agent">
        <instruction>Extract all possible answers from the context snippet that match the question's query.</instruction>
        <input>context_snippet</input>
        <output>candidate_answers</output>
    </operator>
    
    <operator id="3" type="agent">
        <instruction>Verify each candidate answer against the problem statement to ensure relevance and accuracy.</instruction>
        <input>candidate_answers, core_entity</input>
        <output>verified_answers</output>
    </operator>
    
    <operator id="4" type="agent">
        <instruction>Use logical reasoning to eliminate implausible options based on domain knowledge or constraints in the question.</instruction>
        <input>verified_answers</input>
        <output>filtered_answers</output>
    </operator>
    
    <operator id="5" type="agent">
        <instruction>Check for consistency with known facts or patterns in the provided context (e.g., names, roles, affiliations).</instruction>
        <input>filtered_answers, context_snippet</input>
        <output>final_answer</output>
    </operator>
    
    <operator id="6" type="agent">
        <instruction>Validate final answer by cross-referencing with any explicit definitions or associations in the context.</instruction>
        <input>final_answer, context_snippet</input>
        <output>validated_answer</output>
    </operator>
    
    <operator id="7" type="agent">
        <instruction>Ensure the answer is uniquely determined and satisfies all constraints of the original question.</instruction>
        <input>validated_answer</input>
        <output>conclusion</output>
    </operator>