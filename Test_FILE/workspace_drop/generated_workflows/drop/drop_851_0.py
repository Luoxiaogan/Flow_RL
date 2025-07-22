# Workflow ID: drop_851_0
# Benchmark: drop
# Data Indices: [1712, 2345, 601, 2532]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key question and relevant entities in the passage.</instruction>
        <dependencies>1</dependencies>
    </node>
    <node id="3" type="agent">
        <instruction>Extract all numerical values related to the question, focusing on specific metrics (e.g., touchdowns, field goals, distances).</instruction>
        <dependencies>2</dependencies>
    </node>
    <node id="4" type="agent">
        <instruction>Filter values based on the question's constraints (e.g., field goals between 20-30 yards, players with 3 golds ten years apart).</instruction>
        <dependencies>3</dependencies>
    </node>
    <node id="5" type="agent">
        <instruction>Compare extracted values to determine the answer by identifying maximum/minimum or patterns (e.g., longest/shortest field goal, Olympic golds over time).</instruction>
        <dependencies>4</dependencies>
    </node>
    <node id="6" type="output">
        <instruction>Return the final answer derived from step 5.</instruction>
        <dependencies>5</dependencies>
    </node>