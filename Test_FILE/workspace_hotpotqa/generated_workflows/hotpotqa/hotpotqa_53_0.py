# Workflow ID: hotpotqa_53_0
# Benchmark: hotpotqa
# Data Indices: [1336, 3900, 595, 1927, 426]

<operator id="0">
        <instruction>Identify the key elements in the question and determine what information is being sought.</instruction>
        <input>problem</input>
        <output>key_elements</output>
    </operator>
    <operator id="1">
        <instruction>Extract relevant context that directly relates to the key elements identified in the previous step.</instruction>
        <input>key_elements, context</input>
        <output>relevant_context</output>
    </operator>
    <operator id="2">
        <instruction>Process the relevant context to isolate the specific answer or evidence that resolves the question.</instruction>
        <input>relevant_context</input>
        <output>answer_candidate</output>
    </operator>
    <operator id="3">
        <instruction>Verify the answer candidate against all available context to ensure accuracy and completeness.</instruction>
        <input>answer_candidate, context</input>
        <output>verified_answer</output>
    </operator>
    <operator id="4">
        <instruction>Format the verified answer into a concise and clear response.</instruction>
        <input>verified_answer</input>
        <output>final_answer</output>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>