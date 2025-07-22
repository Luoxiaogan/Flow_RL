# Workflow ID: drop_280_0
# Benchmark: drop
# Data Indices: [3740, 1400, 1641, 3044]

<operator id="0">
    <instruction>Identify the key players and their actions in the passage. Focus on scoring plays and their distances.</instruction>
    <input>problem</input>
    <output>parsed_events</output>
  </operator>
  <operator id="1">
    <instruction>From the parsed events, extract all touchdown passes and their yardages.</instruction>
    <input>parsed_events</input>
    <output>touchdown_passes</output>
  </operator>
  <operator id="2">
    <instruction>Determine which touchdown pass had the longest distance by comparing yardages.</instruction>
    <input>touchdown_passes</input>
    <output>longest_touchdown_pass</output>
  </operator>
  <operator id="3">
    <instruction>Extract the receiver's name associated with the longest touchdown pass.</instruction>
    <input>longest_touchdown_pass</input>
    <output>receiver_name</output>
  </operator>
  <operator id="4">
    <instruction>Verify that the extracted receiver is consistent with the passage details to ensure accuracy.</instruction>
    <input>receiver_name, problem</input>
    <output>verified_answer</output>
  </operator>
  <connection from="0" to="1"/>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>