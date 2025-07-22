# Workflow ID: drop_307_0
# Benchmark: drop
# Data Indices: [1843, 1406, 2702, 416]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key data points related to the question. Extract all relevant values or events mentioned in the passage that pertain to the query.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Process the extracted data step-by-step to determine the answer. If multiple values are involved, compare them logically to find the correct result based on the question's requirements.</instruction>
    <input>2</input>
    <output>processed_result</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the processed result by cross-checking against the original passage to ensure accuracy and avoid misinterpretation of context.</instruction>
    <input>3</input>
    <output>verified_result</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>