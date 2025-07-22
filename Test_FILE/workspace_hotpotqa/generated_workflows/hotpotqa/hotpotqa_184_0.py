# Workflow ID: hotpotqa_184_0
# Benchmark: hotpotqa
# Data Indices: [2664, 638, 1170, 3067, 3197]

<agent id="1" type="reasoning">
        <instruction>Identify the key entities in the problem statement that relate to the aerospace industry and the UK. Focus on companies with a large presence in the British aerospace sector.</instruction>
    </agent>
    <agent id="2" type="search">
        <instruction>Find which of these companies is a British multinational public limited company and determine its incorporation date.</instruction>
    </agent>
    <agent id="3" type="verification">
        <instruction>Verify the incorporation date of the identified company by cross-referencing with reliable sources or official records.</instruction>
    </agent>
    <agent id="4" type="aggregation">
        <instruction>Aggregate the verified incorporation date as the final answer, ensuring it aligns with the question's requirement for a British multinational public limited company in the aerospace industry.</instruction>
    </agent>
    <edge from="1" to="2" />
    <edge from="2" to="3" />
    <edge from="3" to="4" />