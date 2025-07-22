# Workflow ID: drop_3_0
# Benchmark: drop
# Data Indices: [3737, 319, 1458, 35]

<node id="start">
    <operator>input_problem</operator>
  </node>
  
  <node id="parse_dates">
    <operator>extract_date_info</operator>
    <edge from="start" to="parse_dates"/>
  </node>

  <node id="calculate_days">
    <operator>compute_day_difference</operator>
    <edge from="parse_dates" to="calculate_days"/>
  </node>

  <node id="validate_result">
    <operator>validate_output_format</operator>
    <edge from="calculate_days" to="validate_result"/>
  </node>

  <node id="output">
    <operator>return_integer_days</operator>
    <edge from="validate_result" to="output"/>
  </node>