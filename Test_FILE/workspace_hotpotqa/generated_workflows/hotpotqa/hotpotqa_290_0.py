# Workflow ID: hotpotqa_290_0
# Benchmark: hotpotqa
# Data Indices: [3195, 3812, 3336, 1952]

<operator id="1">
        <instruction>Identify the core question and extract key entities from the problem statement.</instruction>
        <input>problem</input>
        <output>key_entities, question</output>
    </operator>
    
    <operator id="2">
        <instruction>Retrieve relevant context information associated with each key entity.</instruction>
        <input>key_entities, context</input>
        <output>retrieved_context</output>
    </operator>
    
    <operator id="3">
        <instruction>Process retrieved context to isolate direct answers or supporting evidence for the question.</instruction>
        <input>retrieved_context</input>
        <output>direct_answers</output>
    </operator>
    
    <operator id="4">
        <instruction>Validate each candidate answer against the original question and context for consistency.</instruction>
        <input>direct_answers, question</input>
        <output>validated_answers</output>
    </operator>
    
    <operator id="5">
        <instruction>Aggregate final answer(s) into a concise response format.</instruction>
        <input>validated_answers</input>
        <output>final_answer</output>
    </operator>
    
    <link from="1" to="2"/>
    <link from="2" to="3"/>
    <link from="3" to="4"/>
    <link from="4" to="5"/>