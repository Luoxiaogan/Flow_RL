# Workflow ID: hotpotqa_422_0
# Benchmark: hotpotqa
# Data Indices: [811, 3699, 3774, 691]

<operator id="1">
        <instruction>Identify the key entities and relationships in the problem statement.</instruction>
        <input>problem</input>
        <output>entity_list, relationship_graph</output>
    </operator>
    
    <operator id="2">
        <instruction>Extract relevant context that directly answers the question.</instruction>
        <input>entity_list, relationship_graph, context</input>
        <output>relevant_context</output>
    </operator>
    
    <operator id="3">
        <instruction>Validate the extracted information against known facts or constraints in the context.</instruction>
        <input>relevant_context, problem</input>
        <output>validated_answer</output>
    </operator>
    
    <operator id="4">
        <instruction>Formulate a precise answer based on the validated information.</instruction>
        <input>validated_answer</input>
        <output>final_answer</output>
    </operator>
    
    <operator id="5">
        <instruction>Check for consistency between the final answer and all inputs used in the process.</instruction>
        <input>final_answer, problem, context</input>
        <output>consistency_check</output>
    </operator>
    
    <operator id="6">
        <instruction>Return the final verified answer if consistent; otherwise, flag for review.</instruction>
        <input>final_answer, consistency_check</input>
        <output>result</output>
    </operator>