# Workflow ID: drop_492_0
# Benchmark: drop
# Data Indices: [1032, 1857, 886, 1337, 2628]

<agent id="1" type="extract">
    <instruction>Extract all relevant numerical data and entities from the passage that relate to the question.</instruction>
  </agent>
  <agent id="2" type="process">
    <instruction>Identify the key elements in the question and map them to the extracted data. Determine what needs to be calculated or compared.</instruction>
  </agent>
  <agent id="3" type="compute">
    <instruction>Perform the necessary computation using the mapped data, ensuring each step logically follows from the previous one.</instruction>
  </agent>
  <agent id="4" type="validate">
    <instruction>Verify that the computed result aligns with the constraints of the question and the context of the passage.</instruction>
  </agent>
  <agent id="5" type="synthesize">
    <instruction>Combine the validated result with any contextual information needed to form a complete answer.</instruction>
  </agent>
  <edge from="1" to="2" />
  <edge from="2" to="3" />
  <edge from="3" to="4" />
  <edge from="4" to="5" />