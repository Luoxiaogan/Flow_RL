# Workflow ID: hotpotqa_173_0
# Benchmark: hotpotqa
# Data Indices: [1703, 2129, 2038, 2223, 2826]

<operator id="1">
        <instruction>Identify the key entities and relationships in the problem statement. Break down the question into its core components to determine what information is needed to solve it.</instruction>
        <input>problem</input>
        <output>entity_analysis</output>
    </operator>
    
    <operator id="2">
        <instruction>Based on the entity analysis, locate the specific information that directly answers the question. Focus only on the relevant context provided.</instruction>
        <input>entity_analysis</input>
        <output>relevant_information</output>
    </operator>
    
    <operator id="3">
        <instruction>Verify that the relevant information accurately addresses the question. Cross-check with any contextual clues or related facts to ensure correctness.</instruction>
        <input>relevant_information</input>
        <output>verification</output>
    </operator>
    
    <operator id="4">
        <instruction>Construct a concise and precise answer based on the verified information. Ensure clarity and avoid unnecessary details.</instruction>
        <input>verification</input>
        <output>final_answer</output>
    </operator>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>