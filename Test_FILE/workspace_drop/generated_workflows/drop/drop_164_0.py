# Workflow ID: drop_164_0
# Benchmark: drop
# Data Indices: [3205, 2041, 1921, 1346, 3034]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements to extract from the passage.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the passage that directly answers the question. Think step by step: first locate the relevant section, then identify the exact value or fact needed.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify the extracted information against the context to ensure accuracy and relevance.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Check for any indirect references or calculations required (e.g., percentages, totals, time spans).</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer based on validated information from previous steps.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>