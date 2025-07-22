# Workflow ID: drop_346_0
# Benchmark: drop
# Data Indices: [177, 3386, 2356, 830]

<node id="1" type="input">
        <prompt>Extract the relevant years from the passage for Emperor Aurangzeb's death and Joseph François Dupleix's arrival in India.</prompt>
    </node>
    <node id="2" type="process">
        <prompt>Calculate the difference between the two years to find the number of years between these events.</prompt>
    </node>
    <node id="3" type="output">
        <prompt>Return the calculated number of years as the final answer.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>