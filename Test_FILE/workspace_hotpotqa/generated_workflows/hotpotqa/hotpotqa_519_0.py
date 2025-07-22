# Workflow ID: hotpotqa_519_0
# Benchmark: hotpotqa
# Data Indices: [475, 2062, 3788, 2869]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify the musical instrument played by David Gilmour based on context.</prompt>
    <output>David Gilmour is known as a guitarist, particularly with Pink Floyd.</output>
  </node>
  <node id="3" type="agent">
    <prompt>Identify the musical instrument played by Glenn Bidmead from the provided context.</prompt>
    <output>Glenn Bidmead is described as a guitarist in the context.</output>
  </node>
  <node id="4" type="agent">
    <prompt>Compare both instruments to find the common one.</prompt>
    <output>Both David Gilmour and Glenn Bidmead play the guitar.</output>
  </node>
  <node id="5" type="output">
    <prompt>Return the common musical instrument played by both individuals.</prompt>
    <result>guitar</result>
  </node>
  <edge from="1" to="2"/>
  <edge from="1" to="3"/>
  <edge from="2" to="4"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>