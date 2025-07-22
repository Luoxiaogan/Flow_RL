# Workflow ID: drop_669_0
# Benchmark: drop
# Data Indices: [2347, 604, 2721, 2185]

<node id="1">
    <input>problem</input>
    <output>extract_question_and_context</output>
    <agent>extractor</agent>
  </node>
  <node id="2">
    <input>extract_question_and_context</input>
    <output>identify_key_entities</output>
    <agent>entity_analyzer</agent>
  </node>
  <node id="3">
    <input>identify_key_entities</input>
    <output>map_entities_to_values</output>
    <agent>value_mapper</agent>
  </node>
  <node id="4">
    <input>map_entities_to_values</input>
    <output>compute_answer</output>
    <agent>calculator</agent>
  </node>
  <node id="5">
    <input>compute_answer</input>
    <output>validate_answer</output>
    <agent>validator</agent>
  </node>
  <node id="6">
    <input>validate_answer</input>
    <output>final_answer</output>
    <agent>finalizer</agent>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>