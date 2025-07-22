# Workflow ID: drop_371_0
# Benchmark: drop
# Data Indices: [3065, 1657, 3246, 2654, 860]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    <param name="input">1</param>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the key elements in the question and match them with the extracted data.</instruction>
    <param name="input">2</param>
    <output>matched_elements</output>
  </node>
  <node id="4" type="agent">
    <instruction>Apply logical reasoning or mathematical operations to derive the answer based on matched elements.</instruction>
    <param name="input">3</param>
    <output>derived_answer</output>
  </node>
  <node id="5" type="agent">
    <instruction>Validate the derived answer by cross-checking with original passage context.</instruction>
    <param name="input">4</param>
    <output>validated_answer</output>
  </node>
  <node id="6" type="output">
    <param name="answer">5</param>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>