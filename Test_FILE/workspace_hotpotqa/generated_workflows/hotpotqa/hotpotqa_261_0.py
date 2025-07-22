# Workflow ID: hotpotqa_261_0
# Benchmark: hotpotqa
# Data Indices: [3269, 3797, 1326, 3321, 2197]

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
    <operator>map_entities_to_concepts</operator>
    <input>entities</input>
    <output>concept_map</output>
  </node>
  <node id="4">
    <operator>generate_hypothesis</operator>
    <input>concept_map</input>
    <output>hypothesis</output>
  </node>
  <node id="5">
    <operator>validate_with_evidence</operator>
    <input>hypothesis, filtered_context</input>
    <output>validated_answer</output>
  </node>
  <node id="6">
    <operator>refine_output</operator>
    <input>validated_answer</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>