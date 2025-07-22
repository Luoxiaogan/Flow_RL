# Workflow ID: drop_728_0
# Benchmark: drop
# Data Indices: [2724, 3538, 2565, 1396, 233]

<node id="1">
    <operator>extract_relevant_data</operator>
    <input>problem</input>
    <output>parsed_data</output>
  </node>
  <node id="2">
    <operator>identify_key_metrics</operator>
    <input>parsed_data</input>
    <output>metrics</output>
  </node>
  <node id="3">
    <operator>filter_by_criteria</operator>
    <input>metrics</input>
    <output>filtered_metrics</output>
  </node>
  <node id="4">
    <operator>aggregate_values</operator>
    <input>filtered_metrics</input>
    <output>aggregated_results</output>
  </node>
  <node id="5">
    <operator>compare_and_select</operator>
    <input>aggregated_results</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>