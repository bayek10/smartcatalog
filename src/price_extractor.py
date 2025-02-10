from anthropic import Anthropic
import base64
import json
import os
from dotenv import load_dotenv
import logging
from typing import List, Dict, Optional
from pathlib import Path
# import pandas as pd
import code

logger = logging.getLogger(__name__)

class PriceExtractor:
    def __init__(self, claude_api_key: str, few_shot_examples_dir: str):
        """
        Initialize PriceExtractor with API key and examples directory.
        
        Args:
            claude_api_key: Anthropic API key
            few_shot_examples_dir: Directory containing example images
        """
        self.client = Anthropic(api_key=claude_api_key)
        self.few_shot_examples_dir = Path(few_shot_examples_dir)
        self.few_shot_examples = self._load_few_shot_examples()
        self.system_instruction = "You are a table data extraction system. Process the ENTIRE table and output ALL combinations in JSON format. Do not truncate, summarize, or ask for confirmation. Output the complete data in one response."
        self.prompt_text = """
I want you to parse a furniture pricing table from the image attached and output the data in JSON format.
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
"""
        self.prompt_text2 = """
output:
[{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Ecopelle / C.O.M.","Dimensions_CM":"53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,48","Colli":"2","EUR":"705"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Tessuto / Synthetic nubuck / Micro nubuck / C.O.L","Dimensions_CM":"53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,48","Colli":"2","EUR":"738"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Pelle","Dimensions_CM":"53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,48","Colli":"2","EUR":"818"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Pelle Glove","Dimensions_CM":"53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,48","Colli":"2","EUR":"858"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Ecopelle / C.O.M.","Dimensions_CM":"B 53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,36","Colli":"1","EUR":"818"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Tessuto / Synthetic nubuck / Micro nubuck / C.O.L","Dimensions_CM":"B 53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,36","Colli":"1","EUR":"871"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Pelle","Dimensions_CM":"B 53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,36","Colli":"1","EUR":"972"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Pelle Glove","Dimensions_CM":"B 53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,36","Colli":"1","EUR":"1.023"}]
</example>

<example>
input:
"""
        self.prompt_text3 = """
output:
[{"Top":"NC / RB","Base":"GFM69 / GFM73 - 06","Dimensions_CM":"B 250x128x75h","Dimensions_INCHES":"98³/₈x50³/₈x29¹/₂h","M3":"1,05","Colli":"3","EUR":"3.570"},{"Top":"NC / RB","Base":"GFM11 / GFM18 - 06","Dimensions_CM":"B 250x128x75h","Dimensions_INCHES":"98³/₈x50³/₈x29¹/₂h","M3":"1,05","Colli":"3","EUR":"3.589"},{"Top":"NC / RB","Base":"GFM69 / GFM73 - 06","Dimensions_CM":"B 300x128x75h","Dimensions_INCHES":"118¹/₈x50³/₈x29¹/₂h","M3":"1,13","Colli":"4","EUR":"3.719"},{"Top":"NC / RB","Base":"GFM11 / GFM18 - 06","Dimensions_CM":"B 300x128x75h","Dimensions_INCHES":"118¹/₈x50³/₈x29¹/₂h","M3":"1,13","Colli":"4","EUR":"3.738"}]
</example>

<example>
input:
"""
        self.prompt_text4 = """
output:
[{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"220V","Dimensions_CM":"S1 ø62x66h","Dimensions_INCHES":"ø24³/₈x26h","M3":"0,33","Colli":"1","EUR":"764"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"110V","Dimensions_CM":"S1 ø62x66h","Dimensions_INCHES":"ø24³/₈x26h","M3":"0,33","Colli":"1","EUR":"787"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"220V","Dimensions_CM":"S2 ø82x73h","Dimensions_INCHES":"ø32¹/₄x28³/₄h","M3":"0,67","Colli":"1","EUR":"1.313"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"110V","Dimensions_CM":"S2 ø82x73h","Dimensions_INCHES":"ø32¹/₄x28³/₄h","M3":"0,67","Colli":"1","EUR":"1.351"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"220V","Dimensions_CM":"P1 ø62x138h","Dimensions_INCHES":"ø24³/₈x54³/₈h","M3":"0,74","Colli":"1","EUR":"1.082"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"110V","Dimensions_CM":"P1 ø62x138h","Dimensions_INCHES":"ø24³/₈x54³/₈h","M3":"0,74","Colli":"1","EUR":"1.112"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"220V","Dimensions_CM":"P2 ø82x149h","Dimensions_INCHES":"ø32¹/₄x58⁵/₈h","M3":"1,34","Colli":"1","EUR":"1.455"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"110V","Dimensions_CM":"P2 ø82x149h","Dimensions_INCHES":"ø32¹/₄x58⁵/₈h","M3":"1,34","Colli":"1","EUR":"1.500"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"220V","Dimensions_CM":"Cavo aggiuntivo 1 mt versione S","EUR":"17"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"110V","Dimensions_CM":"Cavo aggiuntivo 1 mt versione S","EUR":"39"}]
</example>
</examples>
"""
        
    def _load_few_shot_examples(self) -> List[Dict]:
        """Load few-shot example configurations"""
        return [
            {
                "input_text": "EXAMPLE 2:",
                "image_path": str(self.few_shot_examples_dir / "table-image-chair.png"),
                "output": """[{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Ecopelle / C.O.M.","Dimensions_CM":"53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,48","Colli":"2","EUR":"705"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Tessuto / Synthetic nubuck / Micro nubuck / C.O.L","Dimensions_CM":"53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,48","Colli":"2","EUR":"738"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Pelle","Dimensions_CM":"53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,48","Colli":"2","EUR":"818"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Pelle Glove","Dimensions_CM":"53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,48","Colli":"2","EUR":"858"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Ecopelle / C.O.M.","Dimensions_CM":"B 53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,36","Colli":"1","EUR":"818"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Tessuto / Synthetic nubuck / Micro nubuck / C.O.L","Dimensions_CM":"B 53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,36","Colli":"1","EUR":"871"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Pelle","Dimensions_CM":"B 53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,36","Colli":"1","EUR":"972"},{"Telaio":"frN / frNC / frRB / fr71 / fr73","Seduta":"Pelle Glove","Dimensions_CM":"B 53,5x59x86h","Dimensions_INCHES":"21¹/₈x23¹/₄x33⁷/₈h","M3":"0,36","Colli":"1","EUR":"1.023"}]"""
            },
            {
                "input_text": "EXAMPLE 1:",
                "image_path": str(self.few_shot_examples_dir / "table-image-desk2.png"),
                "output": """[{"Top":"NC / RB","Base":"GFM69 / GFM73 - 06","Dimensions_CM":"B 250x128x75h","Dimensions_INCHES":"98³/₈x50³/₈x29¹/₂h","M3":"1,05","Colli":"3","EUR":"3.570"},{"Top":"NC / RB","Base":"GFM11 / GFM18 - 06","Dimensions_CM":"B 250x128x75h","Dimensions_INCHES":"98³/₈x50³/₈x29¹/₂h","M3":"1,05","Colli":"3","EUR":"3.589"},{"Top":"NC / RB","Base":"GFM69 / GFM73 - 06","Dimensions_CM":"B 300x128x75h","Dimensions_INCHES":"118¹/₈x50³/₈x29¹/₂h","M3":"1,13","Colli":"4","EUR":"3.719"},{"Top":"NC / RB","Base":"GFM11 / GFM18 - 06","Dimensions_CM":"B 300x128x75h","Dimensions_INCHES":"118¹/₈x50³/₈x29¹/₂h","M3":"1,13","Colli":"4","EUR":"3.738"}]"""
            },
            {
                "input_text": "EXAMPLE 3:",
                "image_path": str(self.few_shot_examples_dir / "table-image-lamp.png"),
                "output": """[{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"220V","Dimensions_CM":"S1 ø62x66h","Dimensions_INCHES":"ø24³/₈x26h","M3":"0,33","Colli":"1","EUR":"764"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"110V","Dimensions_CM":"S1 ø62x66h","Dimensions_INCHES":"ø24³/₈x26h","M3":"0,33","Colli":"1","EUR":"787"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"220V","Dimensions_CM":"S2 ø82x73h","Dimensions_INCHES":"ø32¹/₄x28³/₄h","M3":"0,67","Colli":"1","EUR":"1.313"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"110V","Dimensions_CM":"S2 ø82x73h","Dimensions_INCHES":"ø32¹/₄x28³/₄h","M3":"0,67","Colli":"1","EUR":"1.351"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"220V","Dimensions_CM":"P1 ø62x138h","Dimensions_INCHES":"ø24³/₈x54³/₈h","M3":"0,74","Colli":"1","EUR":"1.082"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"110V","Dimensions_CM":"P1 ø62x138h","Dimensions_INCHES":"ø24³/₈x54³/₈h","M3":"0,74","Colli":"1","EUR":"1.112"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"220V","Dimensions_CM":"P2 ø82x149h","Dimensions_INCHES":"ø32¹/₄x58⁵/₈h","M3":"1,34","Colli":"1","EUR":"1.455"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"110V","Dimensions_CM":"P2 ø82x149h","Dimensions_INCHES":"ø32¹/₄x58⁵/₈h","M3":"1,34","Colli":"1","EUR":"1.500"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"220V","Dimensions_CM":"Cavo aggiuntivo 1 mt versione S","EUR":"17"},{"Struttura":"OP17 / Nichel","Rivestimento":"Avorio / Marrone / Nero","Impianto":"110V","Dimensions_CM":"Cavo aggiuntivo 1 mt versione S","EUR":"39"}]"""
            }
        ]

    def _encode_image_to_base64(self, image_path: str) -> str:
        """Encode image to base64 for Claude compatibility"""
        with open(image_path, 'rb') as image_file:
            return base64.standard_b64encode(image_file.read()).decode("utf-8")

    def _build_prompt(self, prompt_image: str) -> List[Dict]:
        """Build the complete messages array for Claude"""
        try:
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": self._encode_image_to_base64(prompt_image)
                            },
                        },
                        {
                            "type": "text",
                            "text": self.prompt_text
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": self._encode_image_to_base64(self.few_shot_examples[0]["image_path"])
                            },
                        },
                        {
                            "type": "text",
                            "text": self.prompt_text2
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": self._encode_image_to_base64(self.few_shot_examples[1]["image_path"])
                            },
                        },
                        {
                            "type": "text",
                            "text": self.prompt_text3
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": self._encode_image_to_base64(self.few_shot_examples[2]["image_path"])
                            },
                        },
                        {
                            "type": "text",
                            "text": self.prompt_text4
                        }
                    ],
                }
            ]

            messages.append({"role": "assistant", "content": "["}) # pre-fill response so it can get to the fkn point
            return messages
        except Exception as e:
            logger.error(f"Error building prompt: {str(e)}")
            raise

    def extract_prices(self, table_image_path: str) -> Optional[List[Dict]]:
        """
        Extract price information from a table image.
        
        Args:
            table_image_path: Path to the table image
            
        Returns:
            List of dictionaries containing price information for each combination
        """
        try:
            messages = self._build_prompt(table_image_path)

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                system=self.system_instruction,
                messages=messages,
                temperature=0.5,
                max_tokens=8192
            )

            result = response.content[0].text.strip()
            # code.interact(local=dict(globals(), **locals()))

            # Ensure proper JSON formatting
            if result.startswith("{"):
                result = "[" + result
                
            # Parse and validate JSON
            price_data = json.loads(result)
            logger.info(f"Successfully extracted {len(price_data)} price combinations")
            return price_data

        except Exception as e:
            logger.error(f"Error extracting prices: {str(e)}")
            return None

if __name__ == "__main__":
    # Load environment variables
    load_dotenv("api/.env")
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    # Initialize extractor
    extractor = PriceExtractor(
        claude_api_key=ANTHROPIC_API_KEY,
        few_shot_examples_dir="../few-shot-examples"
    )
    
    # Test with a sample table image
    table_image = "../pdfs/table-image-desk3.png"
    price_data = extractor.extract_prices(table_image)
    
    # code.interact(local=dict(globals(), **locals()))
    
    if price_data:
        print(f"\nExtracted {len(price_data)} price combinations:")
        # print(pd.DataFrame.from_records(price_data))
    else:
        print("Failed to extract price data")
