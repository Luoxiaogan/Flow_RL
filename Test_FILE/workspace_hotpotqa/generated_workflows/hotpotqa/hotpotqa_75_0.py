# Workflow ID: hotpotqa_75_0
# Benchmark: hotpotqa
# Data Indices: [383, 3385, 2863, 1107]

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
    <operator>map_entities_to_types</operator>
    <input>entities</input>
    <output>entity_types</output>
  </node>
  <node id="4">
    <operator>validate_and_filter</operator>
    <input>entity_types</input>
    <output>valid_types</output>
  </node>
  <node id="5">
    <operator>generate_answer</operator>
    <input>valid_types</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>