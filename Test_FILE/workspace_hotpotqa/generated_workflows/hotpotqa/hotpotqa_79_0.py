# Workflow ID: hotpotqa_79_0
# Benchmark: hotpotqa
# Data Indices: [2596, 1616, 3437, 557, 3916]

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
    <operator>map_entities_to_knowledge</operator>
    <input>entities</input>
    <output>knowledge_links</output>
  </node>
  <node id="4">
    <operator>validate_and_filter</operator>
    <input>knowledge_links</input>
    <output>valid_answers</output>
  </node>
  <node id="5">
    <operator>synthesize_final_answer</operator>
    <input>valid_answers</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>