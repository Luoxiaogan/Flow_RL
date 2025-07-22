# Workflow ID: drop_629_0
# Benchmark: drop
# Data Indices: [2739, 1459, 3786, 1522, 2951]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical values related to male and female full-time worker incomes from the passage.</instruction>
        <input>1</input>
        <output>male_income, female_income</output>
    </node>
    <node id="3" type="agent">
        <instruction>Compare the median incomes of male and female full-time workers to determine which is lower.</instruction>
        <input>2</input>
        <output>lower_income_group</output>
    </node>
    <node id="4" type="output">
        <instruction>Return the group with the lower median income.</instruction>
        <input>3</input>
        <output>result</output>
    </node>