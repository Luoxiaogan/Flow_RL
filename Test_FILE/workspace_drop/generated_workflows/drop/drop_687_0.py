# Workflow ID: drop_687_0
# Benchmark: drop
# Data Indices: [3624, 3846, 326, 1844]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key question and relevant data in the passage. Think step by step to isolate the exact information needed to answer the question.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Extract numerical or categorical values from the passage that directly relate to the question. If multiple values are present, determine which one is most relevant to the query.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="operator">
    <operation>filter</operation>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="agent">
    <instruction>Perform necessary arithmetic or logical operations to derive the final answer. Ensure all steps are traceable and correct.</instruction>
    <input>4</input>
    <output>5</output>
  </node>
  <node id="6" type="output">
    <input>5</input>
  </node>