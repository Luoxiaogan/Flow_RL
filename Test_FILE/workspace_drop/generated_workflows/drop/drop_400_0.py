# Workflow ID: drop_400_0
# Benchmark: drop
# Data Indices: [2835, 1269, 28, 2103, 800]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="process">
        <description>Parse the passage to extract scoring events (touchdowns, field goals, safeties)</description>
        <dependencies>1</dependencies>
    </node>
    <node id="3" type="process">
        <description>Identify all touchdowns and their yardages for each team</description>
        <dependencies>2</dependencies>
    </node>
    <node id="4" type="process">
        <description>Identify all field goals and their yardages</description>
        <dependencies>2</dependencies>
    </node>
    <node id="5" type="process">
        <description>Identify any safeties and their scorers</description>
        <dependencies>2</dependencies>
    </node>
    <node id="6" type="process">
        <description>For touchdown questions: Match player names to scoring plays and determine quarters</description>
        <dependencies>3</dependencies>
    </node>
    <node id="7" type="process">
        <description>For yardage questions: Sum relevant scores (e.g., first three scoring drives)</description>
        <dependencies>3,4</dependencies>
    </node>
    <node id="8" type="process">
        <description>For comparison questions (e.g., more touchdowns): Count touchdowns per team and compute difference</description>
        <dependencies>3</dependencies>
    </node>
    <node id="9" type="process">
        <description>For shortest field goals: Sort field goals by yardage and select the two smallest</description>
        <dependencies>4</dependencies>
    </node>
    <node id="10" type="output">
        <description>Return final answer based on question type and processed data</description>
        <dependencies>6,7,8,9</dependencies>
    </node>