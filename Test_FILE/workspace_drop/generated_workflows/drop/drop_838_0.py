# Workflow ID: drop_838_0
# Benchmark: drop
# Data Indices: [3559, 3788, 1314, 1575]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract all touchdown pass yardages from the passage. List each one separately.</instruction>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <instruction>Sum all the extracted touchdown pass yardages to get the total yards of touchdown passes in the game.</instruction>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="output">
        <connect_to>3</connect_to>
    </node>