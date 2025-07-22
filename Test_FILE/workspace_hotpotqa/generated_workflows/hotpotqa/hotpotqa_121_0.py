# Workflow ID: hotpotqa_121_0
# Benchmark: hotpotqa
# Data Indices: [862, 3061, 105, 1667]

<operator id="0" type="agent">
        <instruction>Identify the key entities in the question and their relationships. Break down the problem into smaller components for analysis.</instruction>
    </operator>
    <operator id="1" type="agent">
        <instruction>Extract relevant information from the context that directly relates to the entities identified in step 0. Focus only on data that supports answering the question.</instruction>
    </operator>
    <operator id="2" type="agent">
        <instruction>Compare the extracted information across all relevant entities to determine which one satisfies the condition or criterion in the question.</instruction>
    </operator>
    <operator id="3" type="agent">
        <instruction>Validate your comparison by cross-referencing with any additional supporting facts in the context that reinforce the conclusion.</instruction>
    </operator>
    <operator id="4" type="agent">
        <instruction>Generate a concise final answer based on the validated result, ensuring it directly addresses the original question without unnecessary details.</instruction>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>