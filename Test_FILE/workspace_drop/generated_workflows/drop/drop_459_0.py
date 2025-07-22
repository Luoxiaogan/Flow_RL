# Workflow ID: drop_459_0
# Benchmark: drop
# Data Indices: [14, 3816, 3319, 1083, 1615]

<agent id="1">
        <instruction>Identify the key numerical data points in the passage relevant to the question.</instruction>
        <output>Extract all numbers and their associated contexts (e.g., distances, percentages, dates).</output>
    </agent>
    <agent id="2">
        <instruction>Filter and isolate values that directly answer the specific question asked.</instruction>
        <output>Match extracted numbers to the required metric (e.g., longest pass, total yards, duration).</output>
    </agent>
    <agent id="3">
        <instruction>Perform necessary calculations or comparisons based on the filtered data.</instruction>
        <output>Compute totals, find maximums, or determine durations using the filtered values.</output>
    </agent>
    <agent id="4">
        <instruction>Validate the result against the context of the question to ensure correctness.</instruction>
        <output>Confirm the answer aligns with the question's intent and the passage details.</output>
    </agent>
    <agent id="5">
        <instruction>Format the final answer clearly and concisely for the user.</instruction>
        <output>Return a single, accurate, and well-formatted response.</output>
    </agent>
    <connect from="1" to="2"/>
    <connect from="2" to="3"/>
    <connect from="3" to="4"/>
    <connect from="4" to="5"/>