# Workflow ID: drop_843_0
# Benchmark: drop
# Data Indices: [1342, 3173, 3951, 440]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="process">
        <description>Parse and extract relevant data from the passage</description>
    </node>
    <node id="3" type="analyze">
        <description>Identify key numerical values and relationships in the context</description>
    </node>
    <node id="4" type="reason">
        <description>Apply logical reasoning to answer the question based on extracted data</description>
    </node>
    <node id="5" type="output">
        <description>Generate final answer</description>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>