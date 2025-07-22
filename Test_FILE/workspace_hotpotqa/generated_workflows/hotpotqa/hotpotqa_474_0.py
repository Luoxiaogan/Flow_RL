# Workflow ID: hotpotqa_474_0
# Benchmark: hotpotqa
# Data Indices: [1097, 603, 2914, 3346]

<start>
    <task>Initialize problem context</task>
    <next>analyze_context</next>
  </start>

  <node id="analyze_context">
    <task>Analyze provided context to extract relevant facts</task>
    <next>identify_key_entities</next>
  </node>

  <node id="identify_key_entities">
    <task>Identify key entities and relationships from the context</task>
    <next>validate_relationships</next>
  </node>

  <node id="validate_relationships">
    <task>Validate that extracted relationships align with known domain knowledge</task>
    <next>generate_solution</next>
  </node>

  <node id="generate_solution">
    <task>Construct a precise answer based on validated relationships</task>
    <next>finalize_output</next>
  </node>

  <node id="finalize_output">
    <task>Format output as a clear, concise response</task>
    <next>end</next>
  </node>

  <end>
    <task>Return final answer</task>
  </end>