# Workflow ID: hotpotqa_118_0
# Benchmark: hotpotqa
# Data Indices: [3816, 2485, 2676, 220, 1754]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context for each entity mentioned in the question.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Compare the extracted information to determine relationships or attributes (e.g., occupation, nationality, birth year).</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Validate the comparison result against known facts or constraints in the context.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Provide a clear, concise answer based on the validated result.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>