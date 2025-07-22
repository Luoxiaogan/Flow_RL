# Workflow ID: drop_201_0
# Benchmark: drop
# Data Indices: [427, 1439, 3764, 2757]

<node id="1">
    <input>problem</input>
    <output>agent_1_output</output>
    <operator>extract_relevant_data</operator>
  </node>
  <node id="2">
    <input>agent_1_output</input>
    <output>agent_2_output</output>
    <operator>analyze_numeric_changes</operator>
  </node>
  <node id="3">
    <input>agent_1_output</input>
    <output>agent_3_output</output>
    <operator>compare_records</operator>
  </node>
  <node id="4">
    <input>agent_1_output</input>
    <output>agent_4_output</output>
    <operator>identify_longest_pass</operator>
  </node>
  <node id="5">
    <input>agent_1_output</input>
    <output>agent_5_output</output>
    <operator>determine_score_at_retirement</operator>
  </node>
  <node id="6">
    <input>agent_2_output, agent_3_output, agent_4_output, agent_5_output</input>
    <output>final_answer</output>
    <operator>combine_results</operator>
  </node>