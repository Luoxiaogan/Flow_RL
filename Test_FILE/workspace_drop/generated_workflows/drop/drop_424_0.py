# Workflow ID: drop_424_0
# Benchmark: drop
# Data Indices: [905, 2970, 1048, 651]

<operator id="1">
    <instruction>Extract all field goal distances from the passage.</instruction>
    <input>problem</input>
    <output>field_goal_distances</output>
  </operator>
  <operator id="2">
    <instruction>Sort the field goal distances in descending order to identify the longest and second longest.</instruction>
    <input>field_goal_distances</input>
    <output>sorted_distances</output>
  </operator>
  <operator id="3">
    <instruction>Calculate the difference between the longest and second longest field goal distances.</instruction>
    <input>sorted_distances</input>
    <output>difference</output>
  </operator>
  <operator id="4">
    <instruction>Return the calculated difference as the final answer.</instruction>
    <input>difference</input>
    <output>final_answer</output>
  </operator>