# Workflow ID: drop_52_0
# Benchmark: drop
# Data Indices: [546, 86, 2808, 2577]

<operator id="0">
        <instruction>Identify all scoring events in the passage and categorize them as touchdowns or field goals.</instruction>
        <input>problem</input>
        <output>scoring_events</output>
    </operator>
    
    <operator id="1">
        <instruction>From the categorized scoring events, extract only the touchdown runs (not passes or returns).</instruction>
        <input>scoring_events</input>
        <output>touchdown_runs</output>
    </operator>
    
    <operator id="2">
        <instruction>Count the total number of touchdowns scored in the game by summing all types: runs, passes, and returns.</instruction>
        <input>scoring_events</input>
        <output>total_touchdowns</output>
    </operator>
    
    <operator id="3">
        <instruction>Determine which players made touchdown runs specifically in the first quarter based on event timing.</instruction>
        <input>scoring_events</input>
        <output>first_quarter_runs</output>
    </operator>
    
    <operator id="4">
        <instruction>Find the longest touchdown run from the list of runs, using yardage as the metric.</instruction>
        <input>touchdown_runs</input>
        <output>longest_run</output>
    </operator>
    
    <operator id="5">
        <instruction>Count how many field goals were made during the entire game.</instruction>
        <input>scoring_events</input>
        <output>field_goals_count</output>
    </operator>
    
    <operator id="6">
        <instruction>Aggregate results: total touchdowns, longest run, and field goals for final output.</instruction>
        <input>total_touchdowns, longest_run, field_goals_count, first_quarter_runs</input>
        <output>final_answer</output>
    </operator>