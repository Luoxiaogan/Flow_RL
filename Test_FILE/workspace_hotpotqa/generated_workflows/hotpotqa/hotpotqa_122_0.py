# Workflow ID: hotpotqa_122_0
# Benchmark: hotpotqa
# Data Indices: [3149, 1020, 1231, 1617, 3795]

<start/>
  <agent id="1" type="extract">
    <instruction>Identify the key entities and relationships in the problem statement. Focus on the team, year, conference, and its headquarters.</instruction>
  </agent>
  <agent id="2" type="lookup">
    <instruction>Determine the headquarters of the athletic conference mentioned in the context related to the team's membership in that year.</instruction>
  </agent>
  <agent id="3" type="verify">
    <instruction>Confirm the accuracy of the city identified by cross-referencing with the provided context about the conference's location.</instruction>
  </agent>
  <agent id="4" type="synthesize">
    <instruction>Combine the verified information into a clear and concise final answer based on the extracted data from the previous steps.</instruction>
  </agent>
  <end/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="end"/>