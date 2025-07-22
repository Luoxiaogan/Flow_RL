# Workflow ID: hotpotqa_420_0
# Benchmark: hotpotqa
# Data Indices: [1479, 3206, 914, 833]

<agent id="1" type="reasoning">
        <instruction>Think step by step to identify the core concept in the question. Break down the problem into smaller logical components.</instruction>
        <input>problem</input>
        <output>step_by_step_analysis</output>
    </agent>
    
    <agent id="2" type="retrieval">
        <instruction>Based on the step-by-step analysis, retrieve relevant context that directly answers the question.</instruction>
        <input>step_by_step_analysis</input>
        <output>relevant_context</output>
    </agent>
    
    <agent id="3" type="verification">
        <instruction>Verify that the retrieved context contains a clear and unambiguous answer to the question. If not, flag for further refinement.</instruction>
        <input>relevant_context</input>
        <output>verified_answer</output>
    </agent>
    
    <agent id="4" type="synthesis">
        <instruction>Combine the verified answer with concise reasoning to produce the final output. Ensure clarity and correctness.</instruction>
        <input>verified_answer</input>
        <output>final_output</output>
    </agent>
    
    <agent id="5" type="validation">
        <instruction>Validate the final output against the original question to ensure it fully addresses what was asked.</instruction>
        <input>final_output</input>
        <output>validated_output</output>
    </agent>