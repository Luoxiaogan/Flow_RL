# Workflow ID: drop_297_0
# Benchmark: drop
# Data Indices: [3271, 3388, 1699, 3610]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="process">
        <instruction>Extract total respondents and Moldovan/Romanian speakers from the passage.</instruction>
        <dependencies>1</dependencies>
    </node>
    <node id="3" type="calculate">
        <operation>Subtract Moldovan/Romanian speakers from total respondents to find non-Moldovan/Romanian speakers.</operation>
        <dependencies>2</dependencies>
    </node>
    <node id="4" type="output">
        <label>Number of people who did not have Moldovan/Romanian as first language</label>
        <dependencies>3</dependencies>
    </node>