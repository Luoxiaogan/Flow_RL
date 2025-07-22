# Workflow ID: hotpotqa_569_0
# Benchmark: hotpotqa
# Data Indices: [2078, 3255, 2697, 758]

<operator id="0">
    <instruction>Identify the key entities and relationships in the input context to determine the correct answer.</instruction>
    <input>problem</input>
    <output>entity_analysis</output>
  </operator>
  <operator id="1">
    <instruction>Extract specific facts relevant to the question from the entity analysis.</instruction>
    <input>entity_analysis</input>
    <output>fact_extraction</output>
  </operator>
  <operator id="2">
    <instruction>Validate the extracted facts against known external knowledge or logical consistency.</instruction>
    <input>fact_extraction</input>
    <output>validation</output>
  </operator>
  <operator id="3">
    <instruction>Construct a precise answer based on validated facts.</instruction>
    <input>validation</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>