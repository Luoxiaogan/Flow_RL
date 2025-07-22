# Workflow ID: hotpotqa_9_0
# Benchmark: hotpotqa
# Data Indices: [3211, 2293, 3311, 350, 3181]

<node id="1" type="input">
        <description>Receive problem context and question</description>
    </node>
    <node id="2" type="agent">
        <instruction>Identify key entities and relationships in the context relevant to the question. Think step by step.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Extract specific facts that directly answer the question from the context. Focus on one fact at a time.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Verify the extracted fact against all available context to ensure accuracy and avoid misinterpretation.</instruction>
    </node>
    <node id="5" type="agent">
        <instruction>Combine verified facts into a coherent answer, ensuring clarity and precision.</instruction>
    </node>
    <node id="6" type="output">
        <description>Return the final answer based on the processed information.</description>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>