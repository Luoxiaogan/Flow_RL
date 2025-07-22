# Workflow ID: hotpotqa_256_0
# Benchmark: hotpotqa
# Data Indices: [3926, 2469, 3100, 921]

<agent id="1">
    <instruction>Identify the relevant entities in the context that relate to the question. Focus on extracting precise numerical or categorical data points that directly answer the query.</instruction>
    <input>problem</input>
    <output>entity_extraction</output>
  </agent>

  <agent id="2">
    <instruction>Compare the extracted values or attributes from the context. Apply logical reasoning to determine which entity satisfies the condition in the question (e.g., taller mountain).</instruction>
    <input>entity_extraction</input>
    <output>comparison_result</output>
  </agent>

  <agent id="3">
    <instruction>Validate the comparison result against known geographical facts or additional context to ensure accuracy. If ambiguity exists, resolve it using authoritative sources or internal consistency checks.</instruction>
    <input>comparison_result</input>
    <output>final_answer</output>
  </agent>

  <edge from="1" to="2"/>
  <edge from="2" to="3"/>