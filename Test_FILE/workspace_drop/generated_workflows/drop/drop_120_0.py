# Workflow ID: drop_120_0
# Benchmark: drop
# Data Indices: [3188, 3357, 374, 2014, 1454]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key question and relevant passage segments. Break down the problem into logical steps.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Extract numerical or categorical data directly related to the question from the passage.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Apply mathematical or logical reasoning to compute the required answer based on extracted data.</instruction>
    </node>
    <node id="5" type="agent">
        <instruction>Validate the computed result against the passage to ensure accuracy and relevance.</instruction>
    </node>
    <node id="6" type="output">
        <description>Return the final answer in a clear, concise format.</description>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>