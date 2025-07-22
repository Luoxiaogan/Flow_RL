# Workflow ID: drop_350_0
# Benchmark: drop
# Data Indices: [90, 3255, 699, 2082, 1619]

<start>
    <task>Extract relevant information from the passage</task>
    <next>identify_key_entities</next>
  </start>

  <node id="identify_key_entities">
    <task>Identify key entities and values related to the question</task>
    <next>filter_relevant_data</next>
  </node>

  <node id="filter_relevant_data">
    <task>Filter data that directly answers the question</task>
    <next>process_numeric_values</next>
  </node>

  <node id="process_numeric_values">
    <task>Perform necessary arithmetic or comparison operations on numeric values</task>
    <next>validate_solution</next>
  </node>

  <node id="validate_solution">
    <task>Ensure the computed result matches the context and constraints of the question</task>
    <next>output_final_answer</next>
  </node>

  <node id="output_final_answer">
    <task>Return the final answer as a single, clear value</task>
    <next>end</next>
  </node>

  <end />