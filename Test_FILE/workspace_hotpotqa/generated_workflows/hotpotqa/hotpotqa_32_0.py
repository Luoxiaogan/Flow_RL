# Workflow ID: hotpotqa_32_0
# Benchmark: hotpotqa
# Data Indices: [305, 349, 3815, 1707, 849]

<start>
    <task>Identify the relevant context for the question</task>
    <next>extract_info</next>
  </start>

  <node id="extract_info">
    <task>Extract key details from the context that relate to the question</task>
    <next>analyze_relationships</next>
  </node>

  <node id="analyze_relationships">
    <task>Map relationships between entities in the extracted information</task>
    <next>validate_hypotheses</next>
  </node>

  <node id="validate_hypotheses">
    <task>Check each hypothesis against the context to determine correctness</task>
    <next>generate_answer</next>
  </node>

  <node id="generate_answer">
    <task>Construct a precise answer based on validated hypotheses</task>
    <next>end</next>
  </node>

  <end>
    <task>Return the final answer</task>
  </end>