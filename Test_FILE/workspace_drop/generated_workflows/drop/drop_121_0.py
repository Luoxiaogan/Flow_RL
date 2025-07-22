# Workflow ID: drop_121_0
# Benchmark: drop
# Data Indices: [705, 1425, 3160, 3551]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    
    <node id="2" type="process">
        <description>Extract key numerical values from the passage</description>
        <depends_on>1</depends_on>
    </node>
    
    <node id="3" type="process">
        <description>Compare values to answer the question</description>
        <depends_on>2</depends_on>
    </node>
    
    <node id="4" type="output">
        <description>Return the correct answer based on comparison</description>
        <depends_on>3</depends_on>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>