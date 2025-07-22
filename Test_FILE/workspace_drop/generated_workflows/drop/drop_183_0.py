# Workflow ID: drop_183_0
# Benchmark: drop
# Data Indices: [2611, 2131, 3163, 85, 2812]

<node id="1">
    <operator>extract_years</operator>
    <input>problem</input>
    <output>years</output>
  </node>
  <node id="2">
    <operator>calculate_difference</operator>
    <input>years</input>
    <output>result</output>
  </node>
  <node id="3">
    <operator>validate_result</operator>
    <input>result</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>