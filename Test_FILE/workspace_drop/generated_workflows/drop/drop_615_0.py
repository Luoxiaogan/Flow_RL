# Workflow ID: drop_615_0
# Benchmark: drop
# Data Indices: [1773, 3667, 332, 1770]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    
    <node id="2" type="agent">
        <description>Identify key numerical data in the passage relevant to the question</description>
        <operator>extract_numerical_data</operator>
    </node>
    
    <node id="3" type="agent">
        <description>Process extracted data to answer the specific question</description>
        <operator>process_for_answer</operator>
    </node>
    
    <node id="4" type="output">
        <description>Return the final answer</description>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>