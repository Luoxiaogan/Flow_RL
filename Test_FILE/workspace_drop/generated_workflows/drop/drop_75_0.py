# Workflow ID: drop_75_0
# Benchmark: drop
# Data Indices: [234, 3516, 1037, 3681]

<node id="1">
    <input>problem</input>
    <output>extract_question_and_passage</output>
    <agent>extractor</agent>
  </node>
  <node id="2">
    <input>extract_question_and_passage</input>
    <output>analyze_question_type</output>
    <agent>classifier</agent>
  </node>
  <node id="3">
    <input>analyze_question_type</input>
    <output>identify_key_information</output>
    <agent>locator</agent>
  </node>
  <node id="4">
    <input>identify_key_information</input>
    <output>apply_logical_reasoning</output>
    <agent>reasoner</agent>
  </node>
  <node id="5">
    <input>apply_logical_reasoning</input>
    <output>validate_solution</output>
    <agent>verifier</agent>
  </node>
  <node id="6">
    <input>validate_solution</input>
    <output>generate_final_answer</output>
    <agent>answerer</agent>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>