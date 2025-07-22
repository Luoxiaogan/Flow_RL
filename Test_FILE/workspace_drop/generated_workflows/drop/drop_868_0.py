# Workflow ID: drop_868_0
# Benchmark: drop
# Data Indices: [61, 2888, 3485, 1316]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="process">
        <description>Parse and extract key data points relevant to the question</description>
    </node>
    <node id="3" type="reasoning">
        <description>Apply logical reasoning based on extracted data to answer the question step-by-step</description>
    </node>
    <node id="4" type="validate">
        <description>Verify correctness of the reasoning against known constraints or rules in the passage</description>
    </node>
    <node id="5" type="output">
        <description>Generate final answer based on validated reasoning</description>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>