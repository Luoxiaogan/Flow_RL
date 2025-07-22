# Workflow ID: hotpotqa_550_0
# Benchmark: hotpotqa
# Data Indices: [927, 1431, 2723, 504, 1709]

<operator id="0" type="agent">
        <instruction>Think step by step to identify the key elements in the problem. Extract relevant details from the context that directly answer the question.</instruction>
        <input>problem</input>
        <output>step1_output</output>
    </operator>
    
    <operator id="1" type="agent">
        <instruction>Based on step1_output, determine which film is the fifth installment of the "Child's Play" series and confirm it matches the year 2004.</instruction>
        <input>step1_output</input>
        <output>step2_output</output>
    </operator>
    
    <operator id="2" type="agent">
        <instruction>Verify that Tony Gardner was involved in the special effects for the film identified in step2_output.</instruction>
        <input>step2_output</input>
        <output>step3_output</output>
    </operator>
    
    <operator id="3" type="agent">
        <instruction>Combine all verified information to produce the final answer: the name of the 2004 supernatural comedy slasher film that is the fifth installment of the sequel.</instruction>
        <input>step3_output</input>
        <output>final_answer</output>
    </operator>
    
    <operator id="4" type="agent">
        <instruction>Double-check that the final_answer matches both the year (2004), genre (supernatural comedy slasher), and position in the series (fifth installment).</instruction>
        <input>final_answer</input>
        <output>verification_result</output>
    </operator>
    
    <operator id="5" type="agent">
        <instruction>If verification_result confirms correctness, return the final_answer. Otherwise, reprocess from step1_output with increased focus on the exact match criteria.</instruction>
        <input>verification_result</input>
        <output>result</output>
    </operator>