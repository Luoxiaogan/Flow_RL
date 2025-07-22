# Workflow ID: drop_79_0
# Benchmark: drop
# Data Indices: [1020, 590, 2342, 1757, 582]

<node id="1" type="input">
        <prompt>Read the passage carefully and identify all field goal events mentioned.</prompt>
    </node>
    <node id="2" type="process">
        <prompt>Extract each field goal instance with its yardage and timing from the passage.</prompt>
        <dependency>1</dependency>
    </node>
    <node id="3" type="filter">
        <prompt>Filter out only the field goals, ignoring touchdowns and other scoring plays.</prompt>
        <dependency>2</dependency>
    </node>
    <node id="4" type="aggregate">
        <prompt>Count the total number of field goals recorded in the passage.</prompt>
        <dependency>3</dependency>
    </node>
    <node id="5" type="output">
        <prompt>Return the total count of field goals as the final answer.</prompt>
        <dependency>4</dependency>
    </node>