# Workflow ID: hotpotqa_233_0
# Benchmark: hotpotqa
# Data Indices: [1859, 2834, 3365, 3964]

<agent id="1" type="reasoning">
    <instruction>Identify the birth years of Donnie Munro and Chris Robinson from the context. Compare the two dates to determine who was born first.</instruction>
  </agent>
  <agent id="2" type="comparison">
    <instruction>Compare the birth years obtained from Agent 1. Return the name of the person born earlier.</instruction>
  </agent>
  <agent id="3" type="verification">
    <instruction>Verify the birth years and the comparison logic used in Agents 1 and 2. Ensure no conflicting data exists in the context.</instruction>
  </agent>
  <agent id="4" type="output">
    <instruction>Based on the verified result, return the name of the person born first.</instruction>
  </agent>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>