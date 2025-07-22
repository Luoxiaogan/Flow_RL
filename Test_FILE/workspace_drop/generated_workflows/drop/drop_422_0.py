# Workflow ID: drop_422_0
# Benchmark: drop
# Data Indices: [298, 109, 516, 1662]

<node id="1" type="input">
    <prompt>Read the passage carefully and identify all scoring events in chronological order.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract each scoring event with team, time (quarter), and details. Ensure no event is missed.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Filter for scoring events in the specified quarter from the question. For example, if the question asks about the second quarter, only keep those events.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>Determine which team scored first in that filtered list by checking the earliest event.</prompt>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <prompt>Return the team that scored first in the specified quarter based on the filtered and ordered list.</prompt>
    <depends_on>4</depends_on>
  </node>