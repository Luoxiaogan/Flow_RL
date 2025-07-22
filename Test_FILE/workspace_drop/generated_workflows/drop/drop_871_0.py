# Workflow ID: drop_871_0
# Benchmark: drop
# Data Indices: [1167, 1697, 2326, 2766]

<agent id="1">
        <instruction>Identify all players mentioned in the passage who scored touchdowns.</instruction>
        <output>list of players</output>
    </agent>
    <agent id="2">
        <instruction>For each player identified, extract the total yards from their touchdowns.</instruction>
        <input>list of players</input>
        <output>dictionary: player -> total touchdown yards</output>
    </agent>
    <agent id="3">
        <instruction>Calculate the difference between David Reed's and Derrick Mason's total touchdown yards.</instruction>
        <input>dictionary: player -> total touchdown yards</input>
        <output>difference in yards</output>
    </agent>
    <agent id="4">
        <instruction>Verify that only touchdowns are considered (not field goals or other plays).</instruction>
        <input>passage</input>
        <output>boolean (True if verified)</output>
    </agent>
    <agent id="5">
        <instruction>Ensure the final answer is an integer representing the yard difference.</instruction>
        <input>difference in yards</input>
        <output>integer</output>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="5"/>
    <edge from="4" to="5"/>