# Workflow ID: hotpotqa_552_0
# Benchmark: hotpotqa
# Data Indices: [2188, 3306, 3620, 188, 1263]

<agent id="1" type="reasoning">
        <instruction>Think step by step to identify the correct answer. First, determine what type of universities Baylor and Duke are based on their descriptions.</instruction>
    </agent>
    <agent id="2" type="classification">
        <instruction>Based on the context provided, classify Baylor University and Duke University into a shared category (e.g., private, public, research, religious-affiliated).</instruction>
    </agent>
    <agent id="3" type="comparison">
        <instruction>Compare the characteristics of both universities to find commonalities that define their type. Focus on institutional affiliation, mission, and academic focus.</instruction>
    </agent>
    <agent id="4" type="verification">
        <instruction>Verify the classification by cross-referencing with known facts about both universities: are they both private? Both research universities? Both affiliated with a religious denomination?</instruction>
    </agent>
    <agent id="5" type="synthesis">
        <instruction>Combine the findings from all previous agents to produce a single, accurate description of the type both universities share.</instruction>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>