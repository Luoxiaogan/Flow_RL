# Workflow ID: drop_197_0
# Benchmark: drop
# Data Indices: [3800, 742, 1956, 2443]

<start>
    <task>Extract relevant events from passage</task>
    <agent>parse_events</agent>
  </start>

  <node id="1">
    <task>Identify truce or treaty events</task>
    <agent>identify_truces</agent>
    <next>2</next>
  </node>

  <node id="2">
    <task>Extract years associated with truces or treaties</task>
    <agent>extract_years</agent>
    <next>3</next>
  </node>

  <node id="3">
    <task>Filter and validate years (numeric, not military campaigns)</task>
    <agent>validate_years</agent>
    <next>4</next>
  </node>

  <node id="4">
    <task>Sort years chronologically</task>
    <agent>sort_years</agent>
    <next>5</next>
  </node>

  <node id="5">
    <task>Return list of years with truces/treaties</task>
    <agent>return_result</agent>
  </node>

  <edge from="start" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>