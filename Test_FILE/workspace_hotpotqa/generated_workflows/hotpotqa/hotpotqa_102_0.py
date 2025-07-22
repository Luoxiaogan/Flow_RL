# Workflow ID: hotpotqa_102_0
# Benchmark: hotpotqa
# Data Indices: [3718, 777, 2404, 364, 3408]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements to focus on.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Break down the question into components. Determine what needs to be compared or identified.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Search for relevant information in the context that directly addresses the question.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Compare or analyze the provided data to determine the correct answer based on the question's requirements.</prompt>
    </node>
    <node id="5" type="agent">
        <prompt>Verify the conclusion by cross-checking with the original context to ensure accuracy.</prompt>
    </node>
    <node id="6" type="output">
        <prompt>Provide the final answer based on the verified analysis.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>