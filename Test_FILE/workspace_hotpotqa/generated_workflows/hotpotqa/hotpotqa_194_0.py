# Workflow ID: hotpotqa_194_0
# Benchmark: hotpotqa
# Data Indices: [2018, 497, 3237, 2626]

<agent id="1" type="extract">
    <instruction>Identify the key entities and relationships in the context that directly answer the question.</instruction>
  </agent>
  <agent id="2" type="filter">
    <instruction>From the extracted entities, filter those relevant to the specific query about the choreographer of Alice Cooper's Welcome to My Nightmare.</instruction>
  </agent>
  <agent id="3" type="resolve">
    <instruction>Use the filtered information to determine the correct choreographer based on the context provided.</instruction>
  </agent>
  <agent id="4" type="validate">
    <instruction>Verify the resolution against the full context to ensure accuracy and consistency.</instruction>
  </agent>
  <agent id="5" type="format">
    <instruction>Format the final answer clearly and concisely for output.</instruction>
  </agent>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>