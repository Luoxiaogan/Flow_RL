# Workflow ID: drop_387_0
# Benchmark: drop
# Data Indices: [1927, 3060, 1171, 1668]

<node id="1" type="input">
        <prompt>Understand the question and identify key metrics to compare.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant numerical data from the passage for comparison.</prompt>
        <dependencies>1</dependencies>
    </node>
    <node id="3" type="agent">
        <prompt>Calculate the difference between the two percentages.</prompt>
        <dependencies>2</dependencies>
    </node>
    <node id="4" type="agent">
        <prompt>Verify that the calculation aligns with the question's requirement (percent difference).</prompt>
        <dependencies>3</dependencies>
    </node>
    <node id="5" type="output">
        <prompt>Return the final percentage difference as the answer.</prompt>
        <dependencies>4</dependencies>
    </node>