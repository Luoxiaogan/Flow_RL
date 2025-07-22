# Workflow ID: drop_493_0
# Benchmark: drop
# Data Indices: [313, 3902, 1678, 1544]

<agent id="1">
    <instruction>Identify all field goal kickers mentioned in the passage and their respective distances.</instruction>
    <output>list of kickers with field goal distances</output>
  </agent>
  <agent id="2">
    <instruction>From the list of field goals, determine the longest field goal kicked in the game.</instruction>
    <output>longest field goal distance</output>
  </agent>
  <agent id="3">
    <instruction>Match the longest field goal to the kicker who made it.</instruction>
    <output>kicker of the longest field goal</output>
  </agent>
  <agent id="4">
    <instruction>Return the name of the kicker who made the longest field goal.</instruction>
    <output>final answer</output>
  </agent>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>