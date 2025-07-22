# Workflow ID: drop_735_0
# Benchmark: drop
# Data Indices: [3995, 2090, 1451, 2576, 1922]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    
    <node id="2" type="process">
        <description>Extract relevant numerical data from passage (e.g., field goals, touchdowns, yardages)</description>
        <dependencies>1</dependencies>
    </node>
    
    <node id="3" type="process">
        <description>Identify the longest and shortest values for the metric in question (e.g., field goal distances or touchdown lengths)</description>
        <dependencies>2</dependencies>
    </node>
    
    <node id="4" type="compute">
        <description>Calculate the difference between the longest and shortest values</description>
        <dependencies>3</dependencies>
    </node>
    
    <node id="5" type="output">
        <description>Return the computed difference as the final answer</description>
        <dependencies>4</dependencies>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>