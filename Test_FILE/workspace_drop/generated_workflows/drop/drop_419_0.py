# Workflow ID: drop_419_0
# Benchmark: drop
# Data Indices: [273, 1015, 221, 3632, 1580]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="process">
        <description>Parse and extract key data from passage</description>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="process">
        <description>Identify relevant numerical values for calculation</description>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="compute">
        <description>Perform arithmetic operations based on question</description>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="validate">
        <description>Check if computed result matches expected logic</description>
        <depends_on>4</depends_on>
    </node>
    <node id="6" type="output">
        <description>Return final answer</description>
        <depends_on>5</depends_on>
    </node>