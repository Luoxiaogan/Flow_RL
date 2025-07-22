# Workflow ID: hotpotqa_193_0
# Benchmark: hotpotqa
# Data Indices: [3104, 1692, 3864, 2369]

<agent id="1" type="extract">
    <instruction>Extract key entities and relationships from the context that are relevant to the question.</instruction>
  </agent>
  <agent id="2" type="filter">
    <instruction>Filter out irrelevant information from the extracted entities, focusing only on those directly related to the question.</instruction>
  </agent>
  <agent id="3" type="reason">
    <instruction>Reason step-by-step: Identify the film based on "a war between babies and puppies" and find its director. Then cross-check if this director also worked on "Flushed Away".</instruction>
  </agent>
  <agent id="4" type="validate">
    <instruction>Validate that the identified director is correct by checking both films' credits in the provided context.</instruction>
  </agent>
  <agent id="5" type="combine">
    <instruction>Combine the validated result into a single coherent answer that directly addresses the question.</instruction>
  </agent>
  <link from="1" to="2"/>
  <link from="2" to="3"/>
  <link from="3" to="4"/>
  <link from="4" to="5"/>