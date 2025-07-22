# Workflow ID: drop_320_0
# Benchmark: drop
# Data Indices: [2775, 3471, 812, 3038]

<node id="1" type="input">
    <prompt>Understand the question and identify key elements.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Think step by step: What information is needed to answer this question? How does it relate to the passage?</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Extract relevant details from the passage that directly address the question.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that all necessary data has been extracted and is accurate.</prompt>
  </node>
  <node id="5" type="agent">
    <prompt>Apply logical reasoning or calculation if required to derive the final answer.</prompt>
  </node>
  <node id="6" type="output">
    <prompt>Provide the final, correct answer based on the analysis.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>