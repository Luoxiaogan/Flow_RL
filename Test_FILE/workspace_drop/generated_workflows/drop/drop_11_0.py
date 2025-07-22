# Workflow ID: drop_11_0
# Benchmark: drop
# Data Indices: [3529, 2966, 2789, 3930]

<agent id="1">
        <instruction>Identify all field goals in the passage and extract their distances.</instruction>
        <output>list of field goal distances</output>
    </agent>
    <agent id="2">
        <instruction>Filter the list to include only field goals longer than 30 yards.</instruction>
        <input>list of field goal distances from agent 1</input>
        <output>filtered list of field goals > 30 yards</output>
    </agent>
    <agent id="3">
        <instruction>Count the number of field goals in the filtered list.</instruction>
        <input>filtered list of field goals > 30 yards from agent 2</input>
        <output>integer count of field goals > 30 yards</output>
    </agent>
    <agent id="4">
        <instruction>Return the final count as the answer to the question.</instruction>
        <input>count from agent 3</input>
        <output>final answer (integer)</output>
    </agent>