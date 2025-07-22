# Workflow ID: hotpotqa_224_0
# Benchmark: hotpotqa
# Data Indices: [1814, 2989, 3605, 3990]

<operator id="0">
        <instruction>Identify the key entities in the problem and determine the specific information being asked.</instruction>
        <input>problem</input>
        <output>key_entities, question_focus</output>
    </operator>
    <operator id="1">
        <instruction>Extract relevant context from the provided text that directly relates to the key entities identified.</instruction>
        <input>context, key_entities</input>
        <output>relevant_context</output>
    </operator>
    <operator id="2">
        <instruction>Parse the relevant context to locate the exact answer to the question.</instruction>
        <input>relevant_context, question_focus</input>
        <output>answer</output>
    </operator>
    <operator id="3">
        <instruction>Validate the answer by cross-checking with other parts of the context to ensure accuracy.</instruction>
        <input>relevant_context, answer</input>
        <output>validated_answer</output>
    </operator>
    <operator id="4">
        <instruction>Format the final answer in a clear and concise manner as required by the problem's question structure.</instruction>
        <input>validated_answer</input>
        <output>final_output</output>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>