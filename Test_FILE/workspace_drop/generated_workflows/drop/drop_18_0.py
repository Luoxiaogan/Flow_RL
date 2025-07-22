# Workflow ID: drop_18_0
# Benchmark: drop
# Data Indices: [2523, 1500, 3502, 214]

<node id="1">
        <task>Extract all touchdown passes from the passage</task>
        <input>problem</input>
        <output>list_of_touchdown_passes</output>
    </node>
    <node id="2">
        <task>Filter touchdown passes made by Jason Campbell</task>
        <input>list_of_touchdown_passes</input>
        <output>campbell_touchdown_passes</output>
    </node>
    <node id="3">
        <task>Format the output to list only the yardage of each pass</task>
        <input>campbell_touchdown_passes</input>
        <output>formatted_output</output>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>