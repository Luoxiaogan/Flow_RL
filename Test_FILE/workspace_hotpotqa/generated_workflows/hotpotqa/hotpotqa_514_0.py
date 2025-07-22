# Workflow ID: hotpotqa_514_0
# Benchmark: hotpotqa
# Data Indices: [2268, 2176, 2305, 2756, 2478]

<operator id="1">
    <instruction>Identify the key entity in the question and locate its context.</instruction>
    <input>problem</input>
    <output>entity_context</output>
  </operator>
  <operator id="2">
    <instruction>Extract relevant details from the context that directly answer the question.</instruction>
    <input>entity_context</input>
    <output>relevant_details</output>
  </operator>
  <operator id="3">
    <instruction>Verify if the extracted details provide a complete and unambiguous answer.</instruction>
    <input>relevant_details</input>
    <output>is_complete_answer</output>
  </operator>
  <operator id="4">
    <instruction>If the answer is incomplete, identify missing information and cross-reference with other context entries.</instruction>
    <input>is_complete_answer</input>
    <output>final_answer</output>
  </operator>
  <operator id="5">
    <instruction>Validate the final answer against all provided context to ensure consistency.</instruction>
    <input>final_answer</input>
    <output>validated_answer</output>
  </operator>
  <operator id="6">
    <instruction>Return the validated answer as the output of the graph.</instruction>
    <input>validated_answer</input>
    <output>answer</output>
  </operator>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>