# Workflow ID: hotpotqa_359_0
# Benchmark: hotpotqa
# Data Indices: [2917, 2354, 3303, 1982, 1761]

<agent id="1">
    <instruction>Identify the key entities and relationships in the problem context.</instruction>
    <output>Extract relevant entities such as names, organizations, and classifications from the provided context.</output>
  </agent>
  <agent id="2">
    <instruction>Map each entity to its correct category or classification based on contextual clues.</instruction>
    <output>Classify each entity (e.g., breeds, journals, airlines) using domain knowledge and explicit definitions in the context.</output>
  </agent>
  <agent id="3">
    <instruction>Validate classifications by cross-referencing with known categories or external knowledge.</instruction>
    <output>Ensure consistency of classifications by checking against established categories like FCI groups, academic journals, or breed types.</output>
  </agent>
  <agent id="4">
    <instruction>Resolve any ambiguities by comparing similar entries across the context.</instruction>
    <output>Use comparative analysis between similar terms (e.g., Poitevin horse vs. Poitevin dog) to disambiguate meanings.</output>
  </agent>
  <agent id="5">
    <instruction>Compile final answer by aggregating validated classifications.</instruction>
    <output>Return a concise, accurate answer based on all prior validations and mappings.</output>
  </agent>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>