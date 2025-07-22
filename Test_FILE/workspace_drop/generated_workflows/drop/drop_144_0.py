# Workflow ID: drop_144_0
# Benchmark: drop
# Data Indices: [1098, 3077, 3961, 3984]

<node id="start" type="input"/>
  <node id="step1" type="agent">
    <prompt>Think step by step: First, identify the key entities and relationships in the problem. What is the main question asking? How can we isolate the relevant information from the passage?</prompt>
  </node>
  <node id="step2" type="agent">
    <prompt>Now that you've identified the core question, determine what specific part of the passage contains the answer. Focus only on the relevant sentence or sentences that directly address the question.</prompt>
  </node>
  <node id="step3" type="agent">
    <prompt>Extract the exact numerical or textual answer from the passage based on your analysis. Be precise—do not infer or approximate unless explicitly supported by the text.</prompt>
  </node>
  <node id="output" type="output"/>
  <edge from="start" to="step1"/>
  <edge from="step1" to="step2"/>
  <edge from="step2" to="step3"/>
  <edge from="step3" to="output"/>