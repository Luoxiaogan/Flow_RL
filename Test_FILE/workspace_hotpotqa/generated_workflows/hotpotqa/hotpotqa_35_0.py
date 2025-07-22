# Workflow ID: hotpotqa_35_0
# Benchmark: hotpotqa
# Data Indices: [2618, 3837, 2491, 851, 731]

<agent id="1" type="extract">
    <instruction>Extract the key entities and relationships from the context that relate to the question.</instruction>
  </agent>
  <agent id="2" type="filter">
    <instruction>Filter out irrelevant information and focus only on the entity mentioned in the question and its direct connections.</instruction>
  </agent>
  <agent id="3" type="map">
    <instruction>Map the filtered entities to potential answers by identifying which one satisfies the condition in the question.</instruction>
  </agent>
  <agent id="4" type="validate">
    <instruction>Validate the candidate answer by cross-referencing with the original context to ensure accuracy.</instruction>
  </agent>
  <agent id="5" type="aggregate">
    <instruction>Aggregate all validated results into a final, coherent answer that directly addresses the question.</instruction>
  </agent>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>