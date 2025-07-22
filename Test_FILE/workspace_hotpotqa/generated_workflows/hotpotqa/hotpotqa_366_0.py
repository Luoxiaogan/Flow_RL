# Workflow ID: hotpotqa_366_0
# Benchmark: hotpotqa
# Data Indices: [1517, 61, 138, 3610]

<agent id="1" type="extract">
        <instruction>Extract the birth year of Gary Numan from the context.</instruction>
    </agent>
    <agent id="2" type="extract">
        <instruction>Extract the birth year of Denise Pearson from the context.</instruction>
    </agent>
    <agent id="3" type="compare">
        <instruction>Compare the birth years from agents 1 and 2 to determine who is older.</instruction>
    </agent>
    <agent id="4" type="format">
        <instruction>Format the result as a string stating the name of the older person.</instruction>
    </agent>