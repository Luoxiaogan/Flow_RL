# Workflow ID: drop_360_0
# Benchmark: drop
# Data Indices: [2320, 2217, 1827, 1395, 2101]

<agent id="1">
        <instruction>Identify all touchdowns and their yardages from the passage.</instruction>
        <output>list of (yardage, type) where type is 'TD'</output>
    </agent>
    <agent id="2">
        <instruction>Identify all field goals and their yardages from the passage.</instruction>
        <output>list of (yardage, type) where type is 'FG'</output>
    </agent>
    <agent id="3">
        <instruction>From agent 1's output, extract the two longest touchdown yardages.</instruction>
        <output>two largest TD yardages</output>
    </agent>
    <agent id="4">
        <instruction>From agent 2's output, extract the two longest field goal yardages.</instruction>
        <output>two largest FG yardages</output>
    </agent>
    <agent id="5">
        <instruction>Add the two longest TDs and two longest FGs together.</instruction>
        <output>sum of the four values</output>
    </agent>
    <connection>
        <from>1</from>
        <to>3</to>
    </connection>
    <connection>
        <from>2</from>
        <to>4</to>
    </connection>
    <connection>
        <from>3</from>
        <to>5</to>
    </connection>
    <connection>
        <from>4</from>
        <to>5</to>
    </connection>