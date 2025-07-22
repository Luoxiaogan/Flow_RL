# Workflow ID: drop_726_0
# Benchmark: drop
# Data Indices: [1343, 366, 1119, 2753]

<node id="1" type="input">
    <instruction>Extract relevant data from the passage based on the question.</instruction>
  </node>
  <node id="2" type="process">
    <instruction>Identify all field goals mentioned in the passage and their distances.</instruction>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="filter">
    <instruction>Filter field goals longer than 40 yards.</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="output">
    <instruction>Return the list of players who kicked field goals longer than 40 yards.</instruction>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="input">
    <instruction>Parse household statistics to identify non-family percentage.</instruction>
  </node>
  <node id="6" type="calculate">
    <instruction>Subtract non-family percentage from 100% to find percent that are not non-families.</instruction>
    <depends_on>5</depends_on>
  </node>
  <node id="7" type="output">
    <instruction>Return the calculated percentage of households that are not non-families.</instruction>
    <depends_on>6</depends_on>
  </node>
  <node id="8" type="input">
    <instruction>Collect all field goal data from the passage, including kicker names and yardages.</instruction>
  </node>
  <node id="9" type="filter">
    <instruction>Filter for field goals in the first half only.</instruction>
    <depends_on>8</depends_on>
  </node>
  <node id="10" type="count">
    <instruction>Count how many field goals each player made in the first half.</instruction>
    <depends_on>9</depends_on>
  </node>
  <node id="11" type="output">
    <instruction>Return the player with the most field goals in the first half.</instruction>
    <depends_on>10</depends_on>
  </node>
  <node id="12" type="input">
    <instruction>Extract scoring details from the passage, focusing on halftime score.</instruction>
  </node>
  <node id="13" type="calculate">
    <instruction>Compute the difference between Jets' and Dolphins' scores at halftime.</instruction>
    <depends_on>12</depends_on>
  </node>
  <node id="14" type="output">
    <instruction>Return the point lead the Jets had at halftime.</instruction>
    <depends_on>13</depends_on>
  </node>