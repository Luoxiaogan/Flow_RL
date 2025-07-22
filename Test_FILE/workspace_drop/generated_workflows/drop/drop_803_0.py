# Workflow ID: drop_803_0
# Benchmark: drop
# Data Indices: [3548, 3822, 239, 3877]

<agent id="1">
        <instruction>Identify all scoring plays in the game and categorize them by type (touchdown, field goal, etc.).</instruction>
        <input>game_passage</input>
        <output>scoring_plays</output>
    </agent>
    <agent id="2">
        <instruction>Count the number of touchdowns from the categorized scoring plays.</instruction>
        <input>scoring_plays</input>
        <output>touchdown_count</output>
    </agent>
    <agent id="3">
        <instruction>Verify that no other scoring types (like field goals or extra points) are mistakenly counted as touchdowns.</instruction>
        <input>scoring_plays</input>
        <output>verification</output>
    </agent>
    <agent id="4">
        <instruction>Aggregate the final count of touchdowns, ensuring accuracy based on verification.</instruction>
        <input>touchdown_count, verification</input>
        <output>final_touchdown_total</output>
    </agent>