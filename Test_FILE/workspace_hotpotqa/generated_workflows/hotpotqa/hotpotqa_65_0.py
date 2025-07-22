# Workflow ID: hotpotqa_65_0
# Benchmark: hotpotqa
# Data Indices: [2057, 600, 3533, 3886]

<agent id="1" type="reasoning">
        <instruction>Think step by step to identify the core category both games belong to based on their mechanics and objectives.</instruction>
        <input>problem</input>
        <output>game_category</output>
    </agent>
    <agent id="2" type="classification">
        <instruction>Determine if Twin Tin Bots and Blockade are both board games, video games, or another type. Focus only on structural and play format similarities.</instruction>
        <input>game_category</input>
        <output>type_match</output>
    </agent>
    <agent id="3" type="verification">
        <instruction>Verify that both games share a common gameplay mechanic such as strategy, turn-based play, or physical movement on a grid.</instruction>
        <input>type_match</input>
        <output>shared_mechanic</output>
    </agent>
    <agent id="4" type="synthesis">
        <instruction>Combine the results from previous agents to produce a concise answer explaining the shared game type and why it applies to both.</instruction>
        <input>shared_mechanic</input>
        <output>final_answer</output>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>