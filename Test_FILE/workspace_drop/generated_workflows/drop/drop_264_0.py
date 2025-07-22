# Workflow ID: drop_264_0
# Benchmark: drop
# Data Indices: [1926, 158, 2817, 2558]

<agent id="1">
    <instruction>Identify the key events related to field goals in the passage.</instruction>
    <output>Extract all instances where a field goal was mentioned and note the kicker's name.</output>
  </agent>
  <agent id="2">
    <instruction>Check if the specified kicker (Jason Elam) is mentioned in the passage.</instruction>
    <output>Determine whether Jason Elam is listed as having kicked any field goals.</output>
  </agent>
  <agent id="3">
    <instruction>If Jason Elam is mentioned, count how many field goals he kicked.</instruction>
    <output>Return the number of field goals kicked by Jason Elam.</output>
  </agent>
  <agent id="4">
    <instruction>If Jason Elam is not mentioned, return 0.</instruction>
    <output>Return 0 as the number of field goals kicked by Jason Elam.</output>
  </agent>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="2" to="4"/>