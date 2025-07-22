# Workflow ID: drop_725_0
# Benchmark: drop
# Data Indices: [1133, 263, 1837, 1204, 107]

<node id="1" type="input">
        <param name="problem" />
    </node>
    <node id="2" type="process">
        <operation>Extract relevant percentages from problem</operation>
        <input>1</input>
    </node>
    <node id="3" type="process">
        <operation>Sum percentages of 65 years or older</operation>
        <input>2</input>
    </node>
    <node id="4" type="process">
        <operation>Calculate percentage not 65 or older</operation>
        <input>3</input>
    </node>
    <node id="5" type="output">
        <param name="result" />
        <input>4</input>
    </node>