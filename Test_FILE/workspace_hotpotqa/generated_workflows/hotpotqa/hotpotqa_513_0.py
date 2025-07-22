# Workflow ID: hotpotqa_513_0
# Benchmark: hotpotqa
# Data Indices: [3781, 2398, 2353, 2873, 3545]

<operator id="1">
        <instruction>Identify the key entities in the question and determine what information is needed to answer it.</instruction>
        <input>question</input>
        <output>entity_identification</output>
    </operator>
    
    <operator id="2">
        <instruction>Extract relevant context related to the identified entities from the provided text.</instruction>
        <input>entity_identification, context</input>
        <output>context_extraction</output>
    </operator>
    
    <operator id="3">
        <instruction>Compare the extracted information to find the common element or relationship required by the question.</instruction>
        <input>context_extraction</input>
        <output>comparison_result</output>
    </operator>
    
    <operator id="4">
        <instruction>Verify that the comparison result directly answers the original question without ambiguity.</instruction>
        <input>comparison_result</input>
        <output>final_answer</output>
    </operator>
    
    <operator id="5">
        <instruction>Ensure all prior steps contribute logically to the final answer; if not, refine the reasoning path.</instruction>
        <input>final_answer</input>
        <output>validated_answer</output>
    </operator>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>