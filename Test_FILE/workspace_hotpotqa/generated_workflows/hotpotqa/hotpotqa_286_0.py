# Workflow ID: hotpotqa_286_0
# Benchmark: hotpotqa
# Data Indices: [3969, 1063, 1495, 2202, 1942]

<operator id="1" type="agent">
        <instruction>Identify the key entities in the problem and determine what specific information is being requested.</instruction>
        <input>problem</input>
        <output>entity_extraction</output>
    </operator>
    
    <operator id="2" type="agent">
        <instruction>Locate the context that contains information directly related to the entity identified in step 1. Focus on sentences or phrases that provide the answer.</instruction>
        <input>entity_extraction, context</input>
        <output>context_retrieval</output>
    </operator>
    
    <operator id="3" type="agent">
        <instruction>Extract the exact value or date from the retrieved context that answers the question. If multiple values exist, choose the one most relevant to the query.</instruction>
        <input>context_retrieval</input>
        <output>answer_extraction</output>
    </operator>
    
    <operator id="4" type="agent">
        <instruction>Verify that the extracted answer matches the question's requirements and does not contain extraneous details. Ensure clarity and correctness.</instruction>
        <input>answer_extraction</input>
        <output>final_answer</output>
    </operator>
    
    <operator id="5" type="agent">
        <instruction>Double-check the logic flow: Did we correctly identify the entity, retrieve the right context, and extract the accurate value? Confirm no steps were skipped or misinterpreted.</instruction>
        <input>final_answer</input>
        <output>validation</output>
    </operator>
    
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>
    <connection from="4" to="5"/>