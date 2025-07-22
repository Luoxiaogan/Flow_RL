# Workflow ID: drop_135_0
# Benchmark: drop
# Data Indices: [2696, 2469, 1184, 3687]

<operator id="0" type="extract">
    <instruction>Extract the key dates and events from the passage that relate to the timeline of the conflict and peace treaty.</instruction>
  </operator>
  <operator id="1" type="process">
    <instruction>Identify the year of the invasion of the Neumark and the year the peace treaty was signed. Calculate the difference between these two years.</instruction>
  </operator>
  <operator id="2" type="validate">
    <instruction>Verify that the calculated number of years is accurate by cross-checking with the passage for any explicit or implied time intervals.</instruction>
  </operator>
  <operator id="3" type="output">
    <instruction>Return the final number of years that passed between the invasion of the Neumark and the signing of the peace treaty.</instruction>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>