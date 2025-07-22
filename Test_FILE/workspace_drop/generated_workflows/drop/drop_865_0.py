# Workflow ID: drop_865_0
# Benchmark: drop
# Data Indices: [2170, 2359, 2853, 2327, 2324]

<node id="1">
        <operator>extract_relevant_data</operator>
        <input>problem</input>
        <output>filtered_data</output>
    </node>
    <node id="2">
        <operator>identify_key_events</operator>
        <input>filtered_data</input>
        <output>key_events</output>
    </node>
    <node id="3">
        <operator>calculate_totals</operator>
        <input>key_events</input>
        <output>total_points</output>
    </node>
    <node id="4">
        <operator>validate_solution</operator>
        <input>total_points</input>
        <output>final_answer</output>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>