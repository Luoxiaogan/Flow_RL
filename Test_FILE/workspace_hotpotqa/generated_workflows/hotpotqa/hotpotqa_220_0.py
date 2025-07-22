# Workflow ID: hotpotqa_220_0
# Benchmark: hotpotqa
# Data Indices: [1492, 615, 3924, 1989, 1510]

<node id="1" type="input">
    <prompt>Understand the problem and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the question.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Verify that the extracted information directly answers the question.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>Check for any indirect clues or cross-references in the context that might clarify ambiguity.</prompt>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="agent">
    <prompt>Validate the consistency of the answer with known facts from the context.</prompt>
    <depends_on>4</depends_on>
  </node>
  <node id="6" type="output">
    <prompt>Return the final, verified answer based on all prior steps.</prompt>
    <depends_on>5</depends_on>
  </node>