# Workflow ID: drop_813_0
# Benchmark: drop
# Data Indices: [3158, 368, 1058, 2661, 3495]

<node id="1" type="input">
    <question>What is the question asking?</question>
    <context>Extract relevant data from the passage to answer the question.</context>
  </node>
  
  <node id="2" type="agent">
    <instruction>Identify all numerical values related to the query in the passage.</instruction>
    <input>1</input>
    <output>list of candidate values</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Filter out irrelevant values and keep only those that directly relate to the asked quantity (e.g., yardage for field goals or passes).</instruction>
    <input>2</input>
    <output>filtered list</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Find the minimum value from the filtered list if the question asks for the shortest or smallest.</instruction>
    <input>3</input>
    <output>minimum value</output>
  </node>
  
  <node id="5" type="agent">
    <instruction>Determine whether the question compares two averages (like household vs family size) by checking keywords such as "larger", "smaller", or "percent not".</instruction>
    <input>1</input>
    <output>comparison_type</output>
  </node>
  
  <node id="6" type="agent">
    <instruction>If comparison, compare the two provided average values using standard arithmetic comparison.</instruction>
    <input>5</input>
    <output>result_of_comparison</output>
  </node>
  
  <node id="7" type="agent">
    <instruction>If percentage is asked, subtract the given percentage from 100% to get the non-Hispanic/Latino share.</instruction>
    <input>1</input>
    <output>percentage_result</output>
  </node>
  
  <node id="8" type="agent">
    <instruction>Return the final answer based on the result from the appropriate agent (4, 6, or 7).</instruction>
    <input>4,6,7</input>
    <output>final_answer</output>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="1" to="3"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="1" to="5"/>
  <edge from="5" to="6"/>
  <edge from="1" to="7"/>
  <edge from="7" to="8"/>
  <edge from="4" to="8"/>
  <edge from="6" to="8"/>