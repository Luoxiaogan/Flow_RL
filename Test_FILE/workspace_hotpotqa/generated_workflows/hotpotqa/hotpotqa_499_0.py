# Workflow ID: hotpotqa_499_0
# Benchmark: hotpotqa
# Data Indices: [2192, 1294, 1216, 2943]

<agent id="1" type="extract">
        <instruction>Identify the key entities and their relationships in the problem context.</instruction>
    </agent>
    <agent id="2" type="reason">
        <instruction>Reason step by step: Determine what the question is asking, then trace the relevant historical or governmental affiliation based on the provided context.</instruction>
    </agent>
    <agent id="3" type="validate">
        <instruction>Check if both individuals (Sigmund Jähn and Jean-Loup Chrétien) are linked to the same previous government. If not, explain the discrepancy.</instruction>
    </agent>
    <agent id="4" type="combine">
        <instruction>Combine the findings from agents 1–3 into a single coherent answer that addresses the original question.</instruction>
    </agent>
    <agent id="5" type="output">
        <instruction>Output the final answer as a concise statement based on the validated conclusion.</instruction>
    </agent>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>
    <connection from="4" to="5"/>