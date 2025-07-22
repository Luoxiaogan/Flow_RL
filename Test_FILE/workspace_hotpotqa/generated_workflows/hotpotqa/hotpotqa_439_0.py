# Workflow ID: hotpotqa_439_0
# Benchmark: hotpotqa
# Data Indices: [3606, 3618, 1252, 2358, 2548]

<node id="1" type="input">
        <prompt>Understand the problem and identify key entities mentioned.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context that directly answers the question. Focus on specific details like names, locations, or attributes tied to the query.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify the extracted information against the broader context to ensure accuracy and eliminate ambiguity.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Structure the answer in a clear and concise format, matching the expected output type (e.g., name, number, location).</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer based on validated results from previous steps.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>