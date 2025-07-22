# Workflow ID: drop_522_0
# Benchmark: drop
# Data Indices: [3722, 1142, 1966, 1916, 3469]

<start>
    <task>Extract relevant information from input passage</task>
    <next>identify_question_type</next>
  </start>

  <node id="identify_question_type">
    <task>Determine if the question requires numerical computation, comparison, or direct extraction</task>
    <next>process_question</next>
  </node>

  <node id="process_question">
    <task>Apply reasoning based on question type: e.g., compare values, calculate differences, extract exact numbers</task>
    <next>validate_solution</next>
  </node>

  <node id="validate_solution">
    <task>Check if extracted answer matches expected format and logic (e.g., integer for count, correct comparison)</task>
    <next>output_answer</next>
  </node>

  <node id="output_answer">
    <task>Return final answer as a single value (e.g., number, string)</task>
    <next>end</next>
  </node>

  <end/>