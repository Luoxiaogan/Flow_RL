# Workflow ID: drop_502_0
# Benchmark: drop
# Data Indices: [3986, 766, 2145, 1883, 793]

<agent id="1">
        <instruction>Identify all scoring plays in the passage and extract their point values.</instruction>
        <output>list_of_scores</output>
    </agent>
    <agent id="2">
        <instruction>Filter for touchdown passes only and extract their yardage values.</instruction>
        <input>list_of_scores</input>
        <output>touchdown_passes</output>
    </agent>
    <agent id="3">
        <instruction>Sort the touchdown passes by yardage in ascending order to find the shortest ones.</instruction>
        <input>touchdown_passes</input>
        <output>sorted_touchdowns</output>
    </agent>
    <agent id="4">
        <instruction>Take the first three entries from the sorted list (shortest three touchdown passes).</instruction>
        <input>sorted_touchdowns</input>
        <output>shortest_three</output>
    </agent>
    <agent id="5">
        <instruction>Sum the yardage of the three shortest touchdown passes.</instruction>
        <input>shortest_three</input>
        <output>total_yards</output>
    </agent>
    <connect>
        <from>1</from>
        <to>2</to>
    </connect>
    <connect>
        <from>2</from>
        <to>3</to>
    </connect>
    <connect>
        <from>3</from>
        <to>4</to>
    </connect>
    <connect>
        <from>4</from>
        <to>5</to>
    </connect>