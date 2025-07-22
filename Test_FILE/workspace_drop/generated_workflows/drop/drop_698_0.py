# Workflow ID: drop_698_0
# Benchmark: drop
# Data Indices: [2393, 451, 1254, 3689, 3259]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="agent">
        <description>Extract key entities and numerical data from the passage</description>
        <dependencies>1</dependencies>
    </node>
    <node id="3" type="agent">
        <description>Identify the specific question being asked and locate relevant context in the passage</description>
        <dependencies>1</dependencies>
    </node>
    <node id="4" type="agent">
        <description>Match the question to the extracted data; determine if a direct answer exists or requires calculation</description>
        <dependencies>2,3</dependencies>
    </node>
    <node id="5" type="agent">
        <description>Verify consistency between the extracted data and the question's requirements</description>
        <dependencies>4</dependencies>
    </node>
    <node id="6" type="output">
        <description>Return the final answer based on verified information</description>
        <dependencies>5</dependencies>
    </node>
    <edge from="1" to="2"/>
    <edge from="1" to="3"/>
    <edge from="2" to="4"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>