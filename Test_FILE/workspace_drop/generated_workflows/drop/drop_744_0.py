# Workflow ID: drop_744_0
# Benchmark: drop
# Data Indices: [2250, 1163, 2459, 1706]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the relevant information in the passage related to the question. Focus on specific values, names, or metrics that directly answer the query.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Extract numerical values and compare them to determine the highest or lowest value based on the question's requirement (e.g., most field goals, shortest pass, etc.).</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the extracted data by cross-referencing with other parts of the passage to ensure accuracy and avoid misinterpretation.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="agent">
    <instruction>Generate a final answer based on the verified data, ensuring it directly addresses the question without unnecessary details.</instruction>
    <input>4</input>
    <output>5</output>
  </node>
  <node id="6" type="output">
    <input>5</input>
  </node>