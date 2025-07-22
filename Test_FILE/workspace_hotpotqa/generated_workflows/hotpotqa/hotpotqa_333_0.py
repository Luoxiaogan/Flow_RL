# Workflow ID: hotpotqa_333_0
# Benchmark: hotpotqa
# Data Indices: [3824, 2990, 1856, 3287, 2767]

<agent id="1" type="extract">
        <instruction>Extract all relevant information about television series based on H.G. Wells' science fiction novels from the context.</instruction>
    </agent>
    <agent id="2" type="filter">
        <instruction>Filter out any non-television adaptations or non-H.G. Wells works from the extracted data.</instruction>
    </agent>
    <agent id="3" type="validate">
        <instruction>Validate each candidate adaptation to confirm it is a TV series and directly based on an H.G. Wells novel.</instruction>
    </agent>
    <agent id="4" type="count">
        <instruction>Count the number of valid television series that meet the criteria.</instruction>
    </agent>
    <agent id="5" type="aggregate">
        <instruction>Aggregate the count result from the previous agent to produce the final answer.</instruction>
    </agent>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>
    <connection from="4" to="5"/>