# Workflow ID: drop_236_0
# Benchmark: drop
# Data Indices: [2329, 2218, 3236, 1679, 3751]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities or values needed to solve it.</prompt>
  </node>
  
  <node id="2" type="agent">
    <prompt>Extract relevant information from the passage that directly answers the question. Focus only on what is necessary for solving this specific problem.</prompt>
  </node>
  
  <node id="3" type="agent">
    <prompt>Perform any required calculation or comparison based on the extracted data. If comparing, determine which value is greater or the difference between them.</prompt>
  </node>
  
  <node id="4" type="agent">
    <prompt>Verify that your answer logically follows from the passage and matches the question exactly. Ensure no misinterpretation of units, timeframes, or entities.</prompt>
  </node>
  
  <node id="5" type="output">
    <prompt>Return the final answer as a concise, accurate response to the question.</prompt>
  </node>

  <!-- Connections -->
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>