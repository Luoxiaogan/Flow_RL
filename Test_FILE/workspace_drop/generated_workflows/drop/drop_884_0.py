# Workflow ID: drop_884_0
# Benchmark: drop
# Data Indices: [1134, 2098, 3642, 551, 3157]

<node id="1" type="input">
        <prompt>Read the passage carefully and identify the key events and scores in the game.</prompt>
    </node>
    
    <node id="2" type="process">
        <prompt>Extract all scoring plays for both teams, including field goals and touchdowns, with their respective times and point values.</prompt>
    </node>
    
    <node id="3" type="process">
        <prompt>Calculate the total points scored by each team across all quarters.</prompt>
    </node>
    
    <node id="4" type="decision">
        <prompt>Determine which team has the higher total score based on the calculated points.</prompt>
    </node>
    
    <node id="5" type="output">
        <prompt>Return the name of the team that lost the game — the one with the lower total score.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>