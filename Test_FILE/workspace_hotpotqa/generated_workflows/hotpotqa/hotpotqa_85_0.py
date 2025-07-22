# Workflow ID: hotpotqa_85_0
# Benchmark: hotpotqa
# Data Indices: [2346, 2368, 168, 1501]

<operator id="0">
    <instruction>Identify the key entities in the problem and determine what information is needed to solve it.</instruction>
    <input>problem</input>
    <output>key_entities, required_info</output>
  </operator>
  <operator id="1">
    <instruction>Extract relevant details from the context that match the key entities identified.</instruction>
    <input>key_entities, context</input>
    <output>relevant_data</output>
  </operator>
  <operator id="2">
    <instruction>Verify that the extracted data directly answers the question by cross-referencing with the required information.</instruction>
    <input>relevant_data, required_info</input>
    <output>verified_answer</output>
  </operator>
  <operator id="3">
    <instruction>If the answer is not found or ambiguous, search for additional related context or clarify ambiguities step-by-step.</instruction>
    <input>verified_answer, context</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>