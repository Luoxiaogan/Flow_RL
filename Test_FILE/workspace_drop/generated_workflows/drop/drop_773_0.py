# Workflow ID: drop_773_0
# Benchmark: drop
# Data Indices: [3062, 1210, 1714, 1805]

<agent id="1">
        <instruction>Identify the key entities and actions in the passage related to the question. Focus on timelines, roles, and sequences of events.</instruction>
        <output>Extract relevant facts such as who did what, when, and in what order.</output>
    </agent>
    <agent id="2">
        <instruction>Process the extracted facts to determine which entity matches the criteria in the question (e.g., time frame, role, action).</instruction>
        <output>Filter results based on the specific condition asked in the question.</output>
    </agent>
    <agent id="3">
        <instruction>Validate the filtered result by cross-referencing with other parts of the passage to ensure accuracy and avoid misinterpretation.</instruction>
        <output>Confirm the final answer by checking consistency across all relevant information.</output>
    </agent>
    <connect from="1" to="2"/>
    <connect from="2" to="3"/>