# Workflow ID: hotpotqa_355_0
# Benchmark: hotpotqa
# Data Indices: [2854, 184, 3102, 1155, 1925]

<agent id="1" type="reasoning">
    <instruction>Identify the key entities in the question and their relationships. Break down the problem into smaller components.</instruction>
  </agent>
  <agent id="2" type="search">
    <instruction>Find films featuring both Natalie Portman and Stephen Rea. Focus on roles played by Natalie Portman in those films.</instruction>
  </agent>
  <agent id="3" type="verification">
    <instruction>Confirm the film where both actors appear together and verify Natalie Portman's character in that film.</instruction>
  </agent>
  <agent id="4" type="synthesis">
    <instruction>Combine results from previous agents to determine the correct answer. Ensure consistency with known filmographies.</instruction>
  </agent>
  <edge from="1" to="2" />
  <edge from="2" to="3" />
  <edge from="3" to="4" />