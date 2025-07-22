# Workflow ID: drop_779_0
# Benchmark: drop
# Data Indices: [3971, 1548, 3197, 2071, 237]

<agent id="1" type="extract">
        <instruction>Extract all field goal events from the passage, noting the team, quarter, and yardage.</instruction>
        <input>problem</input>
        <output>field_goals</output>
    </agent>
    
    <agent id="2" type="filter">
        <instruction>Filter field goals to separate by team (Eagles and Vikings).</instruction>
        <input>field_goals</input>
        <output>eagles_field_goals, vikings_field_goals</output>
    </agent>
    
    <agent id="3" type="group">
        <instruction>Group field goals by quarter for each team.</instruction>
        <input>eagles_field_goals, vikings_field_goals</input>
        <output>eagles_by_quarter, vikings_by_quarter</output>
    </agent>
    
    <agent id="4" type="combine">
        <instruction>Combine both teams' field goals by quarter into a single structured format.</instruction>
        <input>eagles_by_quarter, vikings_by_quarter</input>
        <output>field_goals_by_quarter</output>
    </agent>
    
    <agent id="5" type="validate">
        <instruction>Validate that all field goals are correctly assigned to quarters and no data is missing.</instruction>
        <input>field_goals_by_quarter</input>
        <output>validated_output</output>
    </agent>
    
    <agent id="6" type="format">
        <instruction>Format the output as a dictionary where keys are quarters and values are lists of tuples (team, yardage).</instruction>
        <input>validated_output</input>
        <output>final_answer</output>
    </agent>