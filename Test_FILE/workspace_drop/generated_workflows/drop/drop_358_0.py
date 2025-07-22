# Workflow ID: drop_358_0
# Benchmark: drop
# Data Indices: [583, 3616, 1176, 2834]

<agent name="Step1_AnalyzePassage">
        <instruction>Read and understand the passage to identify all instances of touchdown passes and the players involved.</instruction>
        <input>problem</input>
        <output>parsed_events</output>
    </agent>

    <agent name="Step2_IdentifyPassConnections">
        <instruction>From the parsed events, extract each touchdown pass and note which player threw it and who caught it.</instruction>
        <input>parsed_events</input>
        <output>pass_connections</output>
    </agent>

    <agent name="Step3_CountPassesPerPlayer">
        <instruction>For each quarterback, count how many times they connected with a receiver for a touchdown.</instruction>
        <input>pass_connections</input>
        <output>pass_counts</output>
    </agent>

    <agent name="Step4_FilterMultiConnectors">
        <instruction>Identify the quarterbacks who connected with receivers more than once for touchdowns.</instruction>
        <input>pass_counts</input>
        <output>multi_touchdown_passers</output>
    </agent>

    <agent name="Step5_ReturnFinalAnswer">
        <instruction>Return the list of quarterbacks who had more than one touchdown pass connection.</instruction>
        <input>multi_touchdown_passers</input>
        <output>final_answer</output>
    </agent>

    <!-- Edges -->
    <edge from="Step1_AnalyzePassage" to="Step2_IdentifyPassConnections"/>
    <edge from="Step2_IdentifyPassConnections" to="Step3_CountPassesPerPlayer"/>
    <edge from="Step3_CountPassesPerPlayer" to="Step4_FilterMultiConnectors"/>
    <edge from="Step4_FilterMultiConnectors" to="Step5_ReturnFinalAnswer"/>