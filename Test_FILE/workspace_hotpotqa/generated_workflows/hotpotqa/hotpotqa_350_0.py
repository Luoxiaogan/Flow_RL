# Workflow ID: hotpotqa_350_0
# Benchmark: hotpotqa
# Data Indices: [903, 1895, 1156, 604]

<operator id="1">
        <instruction>Identify the key entities in the problem and their relationships.</instruction>
        <input>problem</input>
        <output>entities_and_relations</output>
    </operator>
    
    <operator id="2">
        <instruction>Extract relevant facts from the context that directly answer the question.</instruction>
        <input>entities_and_relations, context</input>
        <output>relevant_facts</output>
    </operator>
    
    <operator id="3">
        <instruction>Validate each fact against the question to determine its relevance and accuracy.</instruction>
        <input>relevant_facts</input>
        <output>validated_facts</output>
    </operator>
    
    <operator id="4">
        <instruction>Generate a concise answer based on the validated facts.</instruction>
        <input>validated_facts</input>
        <output>final_answer</output>
    </operator>
    
    <operator id="5">
        <instruction>Verify the final answer by cross-checking with the original problem statement.</instruction>
        <input>final_answer, problem</input>
        <output>verified_answer</output>
    </operator>