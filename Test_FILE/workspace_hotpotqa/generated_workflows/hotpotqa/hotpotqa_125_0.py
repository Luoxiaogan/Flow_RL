# Workflow ID: hotpotqa_125_0
# Benchmark: hotpotqa
# Data Indices: [2556, 2471, 2147, 2903]

<node id="1">
    <operator>extract_context</operator>
    <input>problem</input>
    <output>context_data</output>
  </node>
  <node id="2">
    <operator>identify_key_entities</operator>
    <input>context_data</input>
    <output>entities</output>
  </node>
  <node id="3">
    <operator>filter_relevant_info</operator>
    <input>entities</input>
    <output>filtered_info</output>
  </node>
  <node id="4">
    <operator>reason_step_by_step</operator>
    <input>filtered_info</input>
    <output>reasoning_path</output>
  </node>
  <node id="5">
    <operator>validate_solution</operator>
    <input>reasoning_path</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>