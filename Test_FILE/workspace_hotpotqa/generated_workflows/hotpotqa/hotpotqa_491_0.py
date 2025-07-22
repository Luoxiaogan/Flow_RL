# Workflow ID: hotpotqa_491_0
# Benchmark: hotpotqa
# Data Indices: [1748, 3189, 2515, 2883]

<agent id="1" type="extract">
        <instruction>Identify the main subject and key details from the context provided.</instruction>
        <input>problem</input>
        <output>subject, key_details</output>
    </agent>
    
    <agent id="2" type="reason">
        <instruction>Use logical reasoning to connect the extracted details to answer the question step by step.</instruction>
        <input>subject, key_details</input>
        <output>intermediate_answer</output>
    </agent>
    
    <agent id="3" type="verify">
        <instruction>Check if the intermediate answer matches known facts or constraints in the context.</instruction>
        <input>intermediate_answer, key_details</input>
        <output>final_answer</output>
    </agent>
    
    <agent id="4" type="ensemble">
        <instruction>Combine outputs from all agents to produce a single coherent solution.</instruction>
        <input>intermediate_answer, final_answer</input>
        <output>solution</output>
    </agent>