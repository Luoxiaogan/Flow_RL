# Workflow ID: hotpotqa_58_0
# Benchmark: hotpotqa
# Data Indices: [1589, 3854, 713, 846, 3487]

<operator id="0">
    <instruction>Identify the key entities and relationships in the problem context.</instruction>
    <input>problem</input>
    <output>entity_list</output>
  </operator>
  <operator id="1">
    <instruction>Extract relevant facts about the main subject from the context.</instruction>
    <input>entity_list</input>
    <output>facts</output>
  </operator>
  <operator id="2">
    <instruction>Map each fact to a potential answer or clue based on its relevance.</instruction>
    <input>facts</input>
    <output>clues</output>
  </operator>
  <operator id="3">
    <instruction>Validate each clue against known information or logical consistency.</instruction>
    <input>clues</input>
    <output>valid_clues</output>
  </operator>
  <operator id="4">
    <instruction>Aggregate valid clues into a final, coherent answer.</instruction>
    <input>valid_clues</input>
    <output>answer</output>
  </operator>
  <operator id="5">
    <instruction>Double-check that the answer matches the question exactly.</instruction>
    <input>answer</input>
    <output>final_answer</output>
  </operator>