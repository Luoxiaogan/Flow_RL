# Workflow ID: hotpotqa_368_0
# Benchmark: hotpotqa
# Data Indices: [3119, 1611, 68, 3871]

<node id="1">
    <operator>extract_relevant_info</operator>
    <input>problem</input>
    <output>filtered_context</output>
  </node>
  <node id="2">
    <operator>identify_key_entities</operator>
    <input>filtered_context</input>
    <output>entities</output>
  </node>
  <node id="3">
    <operator>map_entities_to_answers</operator>
    <input>entities</input>
    <output>candidate_answers</output>
  </node>
  <node id="4">
    <operator>validate_answers</operator>
    <input>candidate_answers</input>
    <output>validated_answers</output>
  </node>
  <node id="5">
    <operator>select_final_answer</operator>
    <input>validated_answers</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>