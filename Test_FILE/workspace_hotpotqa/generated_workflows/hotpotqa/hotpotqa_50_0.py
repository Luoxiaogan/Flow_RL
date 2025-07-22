# Workflow ID: hotpotqa_50_0
# Benchmark: hotpotqa
# Data Indices: [3199, 3994, 3486, 1513, 737]

<node id="1" type="input">
        <prompt>Understand the problem and extract key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify the main subject and relevant context from the provided information. Think step by step to determine what is being asked and what must be found.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Search for direct matches or logical connections between the subject and possible answers in the context. Eliminate irrelevant options based on the problem's constraints.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify that the candidate answer satisfies all conditions of the question. If multiple candidates exist, prioritize based on specificity and relevance.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer derived from the previous steps. Ensure it directly addresses the question without extraneous details.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>