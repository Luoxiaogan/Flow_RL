# Workflow ID: hotpotqa_144_0
# Benchmark: hotpotqa
# Data Indices: [3091, 1129, 2535, 3468]

<operator id="1" type="extract">
    <instruction>Extract the key entities and relationships from the context that directly answer the question.</instruction>
  </operator>
  <operator id="2" type="filter">
    <instruction>Filter out irrelevant entities and focus only on those relevant to the specific question asked.</instruction>
  </operator>
  <operator id="3" type="map">
    <instruction>Map each filtered entity to its corresponding role or attribute in the problem context.</instruction>
  </operator>
  <operator id="4" type="reason">
    <instruction>Reason step-by-step: Identify which entity matches the question's criteria based on the mapped relationships.</instruction>
  </operator>
  <operator id="5" type="validate">
    <instruction>Validate the final answer by cross-referencing it with the original context to ensure accuracy.</instruction>
  </operator>
  <operator id="6" type="output">
    <instruction>Output the validated result as a single, clear answer.</instruction>
  </operator>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>
  <connection from="4" to="5"/>
  <connection from="5" to="6"/>