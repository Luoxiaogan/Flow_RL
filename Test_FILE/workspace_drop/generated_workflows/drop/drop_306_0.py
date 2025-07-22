# Workflow ID: drop_306_0
# Benchmark: drop
# Data Indices: [39, 2816, 1674, 3252, 3781]

<node id="1" type="input">
    <param name="problem" />
  </node>
  
  <node id="2" type="agent">
    <instruction>
      Analyze the passage to identify all scoring plays and their types (touchdowns, field goals).
      For each scoring play, extract the yardage if it's a touchdown pass or field goal.
      Focus only on touchdowns for this specific question.
    </instruction>
    <output name="touchdowns" />
  </node>
  
  <node id="3" type="agent">
    <instruction>
      From the list of touchdowns identified in node 2, determine which one has the greatest yardage.
      This requires comparing the yardages of all touchdown passes.
    </instruction>
    <output name="longest_touchdown_pass" />
  </node>
  
  <node id="4" type="agent">
    <instruction>
      Validate that the longest touchdown pass found in node 3 is indeed from a pass play (not a run or interception return).
      If it's not a pass, re-evaluate the data to ensure correct identification.
    </instruction>
    <output name="validated_longest_pass" />
  </node>
  
  <node id="5" type="output">
    <input name="validated_longest_pass" />
  </node>