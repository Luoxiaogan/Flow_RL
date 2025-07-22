# Workflow ID: hotpotqa_324_0
# Benchmark: hotpotqa
# Data Indices: [1375, 931, 1621, 2083]

<operator id="0">
    <instruction>Identify the key entities mentioned in the context that relate to the question.</instruction>
    <input>problem</input>
    <output>entities</output>
  </operator>
  <operator id="1">
    <instruction>For each entity, determine if it matches the subject of the question (e.g., Myles Kennedy or Buffalo Tom).</instruction>
    <input>entities</input>
    <output>matches</output>
  </operator>
  <operator id="2">
    <instruction>Extract nationality information for each matching entity from the context.</instruction>
    <input>matches</input>
    <output>nationalities</output>
  </operator>
  <operator id="3">
    <instruction>Check if both nationalities are American. If yes, return True; otherwise, return False.</instruction>
    <input>nationalities</input>
    <output>result</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>