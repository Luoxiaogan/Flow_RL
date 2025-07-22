# Workflow ID: drop_263_0
# Benchmark: drop
# Data Indices: [3593, 2512, 992, 2919, 3747]

<agent id="1">
    <instruction>Identify the relevant player and action in the passage that answers the question.</instruction>
    <output>Extract the player's name and the specific action (e.g., touchdown runs, field goals, etc.) mentioned in the passage related to the question.</output>
  </agent>
  <agent id="2">
    <instruction>Filter events based on the condition specified in the question (e.g., longer than X yards, number of times, etc.).</instruction>
    <output>Isolate only those instances that meet the numerical or categorical criteria from the question (e.g., field goals >30 yards).</output>
  </agent>
  <agent id="3">
    <instruction>Sum up or count the filtered values to compute the final answer.</instruction>
    <output>Calculate the total number, sum, or count of qualifying events for the final answer.</output>
  </agent>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>