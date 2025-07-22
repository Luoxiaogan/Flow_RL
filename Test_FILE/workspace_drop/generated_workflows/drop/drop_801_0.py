# Workflow ID: drop_801_0
# Benchmark: drop
# Data Indices: [3111, 346, 2568, 2275]

<node id="1" type="input">
    <prompt>Read the passage carefully and identify all instances of touchdown passes or runs mentioned.</prompt>
  </node>
  
  <node id="2" type="agent">
    <prompt>For each touchdown event, extract the name of the player who completed the pass or scored the run, along with the yardage. Organize this as a list of tuples (player, yardage).</prompt>
  </node>
  
  <node id="3" type="agent">
    <prompt>Sort the list of touchdown events by yardage in descending order to determine the longest to shortest.</prompt>
  </node>
  
  <node id="4" type="agent">
    <prompt>Identify the fourth entry in the sorted list (i.e., the fourth longest touchdown). Return only the name of the player who completed that pass.</prompt>
  </node>
  
  <node id="5" type="output">
    <prompt>Return the name of the player who completed the fourth longest touchdown pass based on your analysis.</prompt>
  </node>

  <!-- Edges -->
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>