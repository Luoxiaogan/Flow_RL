# Workflow ID: drop_430_0
# Benchmark: drop
# Data Indices: [2656, 1828, 2212, 2374, 2619]

<node id="1" type="input">
    <prompt>Understand the question and identify key elements to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant numerical data from the passage related to the question. Think step by step: Identify all instances of the quantity mentioned in the question, such as field goals, touchdowns, or percentages.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Process the extracted data to compute the required value. For example, if calculating total yards, sum all field goal distances; if counting touchdowns, count only those with a one-yard distance.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that your computation matches the exact requirement of the question. Double-check for misinterpretation—e.g., ensure you're not including non-one-yard touchdowns or misreading yardage.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final computed answer based on verified logic.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>