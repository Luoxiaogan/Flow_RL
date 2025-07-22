# Workflow ID: drop_228_0
# Benchmark: drop
# Data Indices: [3522, 1219, 1625, 1061, 649]

<node id="1">
        <operator>extract_relevant_info</operator>
        <input>problem</input>
        <output>filtered_data</output>
    </node>
    <node id="2">
        <operator>identify_key_players</operator>
        <input>filtered_data</input>
        <output>key_players</output>
    </node>
    <node id="3">
        <operator>parse_touchdowns</operator>
        <input>filtered_data</input>
        <output>touchdowns</output>
    </node>
    <node id="4">
        <operator>sum_touchdown_yards</operator>
        <input>touchdowns</input>
        <output>total_td_yards</output>
    </node>
    <node id="5">
        <operator>validate_and_format</operator>
        <input>total_td_yards</input>
        <output>final_answer</output>
    </node>
    <edge from="1" to="2"/>
    <edge from="1" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>