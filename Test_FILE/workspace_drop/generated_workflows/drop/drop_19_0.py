# Workflow ID: drop_19_0
# Benchmark: drop
# Data Indices: [518, 3142, 1377, 3532]

<agent id="1">
        <instruction>Identify all field goals mentioned in the passage and extract their yardages.</instruction>
        <output>list of field goal yardages</output>
    </agent>
    <agent id="2">
        <instruction>Filter the field goal yardages to only those in the second half of the game.</instruction>
        <output>list of second-half field goal yardages</output>
    </agent>
    <agent id="3">
        <instruction>Count how many field goals were made in the second half by summing the filtered list.</instruction>
        <output>integer count of second-half field goals</output>
    </agent>
    <agent id="4">
        <instruction>Verify that the count matches the number of field goals kicked by Buehler in the second half, based on the passage.</instruction>
        <output>boolean indicating correctness of the count</output>
    </agent>
    <connect from="1" to="2"/>
    <connect from="2" to="3"/>
    <connect from="3" to="4"/>