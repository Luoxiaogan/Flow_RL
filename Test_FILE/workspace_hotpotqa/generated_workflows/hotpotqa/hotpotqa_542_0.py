# Workflow ID: hotpotqa_542_0
# Benchmark: hotpotqa
# Data Indices: [3200, 3051, 3717, 3010]

<node id="1">
    <operator>extract_relevant_info</operator>
    <input>problem</input>
    <output>filtered_context</output>
  </node>
  <node id="2">
    <operator>identify_key_entities</operator>
    <input>filtered_context</input>
    <output>key_entities</output>
  </node>
  <node id="3">
    <operator>trace_relationships</operator>
    <input>key_entities</input>
    <output>relationships</output>
  </node>
  <node id="4">
    <operator>resolve_target</operator>
    <input>relationships</input>
    <output>answer_candidate</output>
  </node>
  <node id="5">
    <operator>validate_answer</operator>
    <input>answer_candidate</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>