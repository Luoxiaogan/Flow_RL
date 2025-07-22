# Workflow ID: drop_154_0
# Benchmark: drop
# Data Indices: [2927, 608, 3721, 1686]

<agent id="1">
        <instruction>Identify the key event or action in the question that needs to be calculated or determined.</instruction>
        <output>Extract the specific query point: e.g., "how many touchdowns" or "how many yards."</output>
    </agent>
    <agent id="2">
        <instruction>Scan the passage for all instances related to the identified event, focusing on numerical values and relevant context.</instruction>
        <output>Locate all mentions of the subject (e.g., player name, quarter, play type) and associated numbers.</output>
    </agent>
    <agent id="3">
        <instruction>Filter out irrelevant details; retain only data points directly answering the question.</instruction>
        <output>Isolate the exact values needed—e.g., touchdown pass counts in a specific quarter.</output>
    </agent>
    <agent id="4">
        <instruction>Apply arithmetic logic if necessary (e.g., difference between two yardages, sum of counts).</instruction>
        <output>Compute final answer based on filtered data.</output>
    </agent>
    <agent id="5">
        <instruction>Verify the result against the passage to ensure no misinterpretation occurred.</instruction>
        <output>Confirm correctness by cross-checking with original text.</output>
    </agent>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>
    <connection from="4" to="5"/>