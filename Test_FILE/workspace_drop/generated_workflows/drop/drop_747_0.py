# Workflow ID: drop_747_0
# Benchmark: drop
# Data Indices: [1877, 2479, 1796, 2377]

<node id="1" type="input">
        <param>problem</param>
    </node>
    <node id="2" type="agent">
        <instruction>Extract all numerical values related to distances (yards) from the passage. Focus only on values that represent field goals, touchdown passes, or runs.</instruction>
        <input>1</input>
        <output>extracted_values</output>
    </node>
    <node id="3" type="agent">
        <instruction>Filter out only the yardage values for field goals and identify the maximum among them.</instruction>
        <input>2</input>
        <output>max_field_goal</output>
    </node>
    <node id="4" type="agent">
        <instruction>Identify all touchdown pass yardages and determine the longest and shortest among them.</instruction>
        <input>2</input>
        <output>td_passes</output>
    </node>
    <node id="5" type="agent">
        <instruction>Calculate the difference between the longest and shortest touchdown pass yardages.</instruction>
        <input>4</input>
        <output>td_pass_diff</output>
    </node>
    <node id="6" type="agent">
        <instruction>Compare scores in the fourth quarter by identifying all scoring plays (field goals, touchdowns) and summing their points.</instruction>
        <input>1</input>
        <output>fourth_quarter_scores</output>
    </node>
    <node id="7" type="agent">
        <instruction>Determine the duration of a historical war by subtracting the start year from the end year.</instruction>
        <input>1</input>
        <output>war_duration</output>
    </node>
    <node id="8" type="agent">
        <instruction>Return the final answer based on the question: For Problem 1, return the difference between longest and shortest touchdown pass; for Problem 2, return the team with highest score in Q4; for Problem 3, return the war duration; for Problem 4, return the longest field goal.</instruction>
        <input>3,5,6,7</input>
        <output>final_answer</output>
    </node>