**note**: 
1. the below sys instruction & prompt were used to parse tables in the dataset folder using Claude 3.5 sonnet v2
2. the response was pre-filled with a ```{"role": "assistant", "content": "["}``` line to get the model to get to the point
3. below are the model settings used

```
response = self.client.messages.create(
    model="claude-3-5-sonnet-20241022",
    system=self.system_instruction,
    messages=messages,
    temperature=0.5,
    max_tokens=8192
)
```

# SYSTEM_INSTRUCTION
"You are a table data extraction system. Process the ENTIRE table and output ALL combinations in JSON format. Do not truncate, summarize, or ask for confirmation. Output the complete data in one response."

# PROMPT (MESSAGES)
"I want you to parse a furniture pricing table from the image attached and output the data in JSON format.
The table describes combinations of attributes, each represented by row and column headers. Your task is to produce the output below

TASK INPUT: 
An image of a complex table with pricing information based on several attributes, such as color codes, finishing, dimensions, etc.
There might be nested sub-categories and some columns might be combined

TASK OUTPUT: 
A JSON array of objects, where each object represents the price for each combination of attributes in the table. Output the complete list of objects. The JSON format should be:
[
  {
    attribute 1: attribute 1 value,
    attribute 2: attribute 2 value,
    attribute 3: attribute 3 value,
    attribute X: attribute X value,
    price: price in EUR from image
  }
]

<examples>
<example>
input:
{base64 encoded image in path /smartcatalog/few-shot-examples/table-image-chair.png}

output:
[{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Ecopelle / C.O.M.","Dimensions_CM":"53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,48","Colli":"2","EUR":"705"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Tessuto / Synthetic nubuck / Micro nubuck / C.O.L","Dimensions_CM":"53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,48","Colli":"2","EUR":"738"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Pelle","Dimensions_CM":"53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,48","Colli":"2","EUR":"818"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Pelle Glove","Dimensions_CM":"53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,48","Colli":"2","EUR":"858"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Ecopelle / C.O.M.","Dimensions_CM":"B 53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,36","Colli":"1","EUR":"818"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Tessuto / Synthetic nubuck / Micro nubuck / C.O.L","Dimensions_CM":"B 53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,36","Colli":"1","EUR":"871"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Pelle","Dimensions_CM":"B 53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,36","Colli":"1","EUR":"972"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Pelle Glove","Dimensions_CM":"B 53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,36","Colli":"1","EUR":"1.023"}]
</example>

<example>
input:
{base64 encoded image in path /smartcatalog/few-shot-examples/table-image-desk2.png}

output:
[{"Top":"NC / RB","Base":"GFM69 / GFM73 - 06","Dimensions_CM":"B 250x128x75h","Dimensions_INCHES":"98³/₈x50³/₈x29¹/₂h","M3":"1,05","Colli":"3","EUR":"3.570"},{"Top":"NC / RB","Base":"GFM11 / GFM18 - 06","Dimensions_CM":"B 250x128x75h","Dimensions_INCHES":"98³/₈x50³/₈x29¹/₂h","M3":"1,05","Colli":"3","EUR":"3.589"},{"Top":"NC / RB","Base":"GFM69 / GFM73 - 06","Dimensions_CM":"B 300x128x75h","Dimensions_INCHES":"118¹/₈x50³/₈x29¹/₂h","M3":"1,13","Colli":"4","EUR":"3.719"},{"Top":"NC / RB","Base":"GFM11 / GFM18 - 06","Dimensions_CM":"B 300x128x75h","Dimensions_INCHES":"118¹/₈x50³/₈x29¹/₂h","M3":"1,13","Colli":"4","EUR":"3.738"}]
</example>

<example>
input:
{base64 encoded image in path /smartcatalog/few-shot-examples/table-image-lamp.png}

output:
[{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"220V","Dimensions_CM":"S1 ø62x66h","Dimensions_INCHES":"ø24³/₈x26h","M3":"0,33","Colli":"1","EUR":"764"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"110V","Dimensions_CM":"S1 ø62x66h","Dimensions_INCHES":"ø24³/₈x26h","M3":"0,33","Colli":"1","EUR":"787"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"220V","Dimensions_CM":"S2 ø82x73h","Dimensions_INCHES":"ø32¹/₄x28³/₄h","M3":"0,67","Colli":"1","EUR":"1.313"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"110V","Dimensions_CM":"S2 ø82x73h","Dimensions_INCHES":"ø32¹/₄x28³/₄h","M3":"0,67","Colli":"1","EUR":"1.351"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"220V","Dimensions_CM":"P1 ø62x138h","Dimensions_INCHES":"ø24³/₈x54³/₈h","M3":"0,74","Colli":"1","EUR":"1.082"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"110V","Dimensions_CM":"P1 ø62x138h","Dimensions_INCHES":"ø24³/₈x54³/₈h","M3":"0,74","Colli":"1","EUR":"1.112"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"220V","Dimensions_CM":"P2 ø82x149h","Dimensions_INCHES":"ø32¹/₄x58⁵/₈h","M3":"1,34","Colli":"1","EUR":"1.455"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"110V","Dimensions_CM":"P2 ø82x149h","Dimensions_INCHES":"ø32¹/₄x58⁵/₈h","M3":"1,34","Colli":"1","EUR":"1.500"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"220V","Dimensions_CM":"Cavo aggiuntivo 1 mt versione S","EUR":"17"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"110V","Dimensions_CM":"Cavo aggiuntivo 1 mt versione S","EUR":"39"}]
</example>
</examples>
"