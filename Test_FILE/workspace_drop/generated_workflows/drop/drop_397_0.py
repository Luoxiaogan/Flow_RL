# Workflow ID: drop_397_0
# Benchmark: drop
# Data Indices: [2719, 2593, 491, 2711]

<agent id="1">
        <instruction>Identify the relevant numerical values from the passage related to the question.</instruction>
        <input>problem</input>
        <output>retrieved_values</output>
    </agent>
    
    <agent id="2">
        <instruction>Extract the specific yardage for the field goal made by Prater and the second field goal made by Folk.</instruction>
        <input>retrieved_values</input>
        <output>field_goal_yards</output>
    </agent>
    
    <agent id="3">
        <instruction>Calculate the absolute difference between the two field goal distances.</instruction>
        <input>field_goal_yards</input>
        <output>difference</output>
    </agent>
    
    <agent id="4">
        <instruction>Verify that the calculation is correct and matches the question's requirement.</instruction>
        <input>difference</input>
        <output>final_answer</output>
    </agent>