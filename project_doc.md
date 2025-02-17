# PROJECT CONTEXT:
I'm building a project. This one solves an expensive, time-consuming and painful problem that my friend faces in his company and he asked if i could help him.
For context, he works at an italian outfitting and supply company that does high-end work in Dubai for villas on the palm jumeirah among other luxury commercial and residential projects.
The company serves both clients and designers with their needs, supplying hundreds of brands each with hundreds or thousands of SKUs. But it is not digitized. 
Almost all of the brand catalogues are in PDF form with hundreds of pages each, that contain details like product name, dimension diagrams, price tables and descriptions for each product. 
So each time a project needs to be done, the designers and architects go through many pdfs and many items to find either the right set of items that match the style preferences of a client for review, or even just to find the price for a specific item that the client already has selected as their choice. 
I'm building a solution to this problem and have my friends company start using it asap. 

# BILL OF QUANTITIES (BoQ):
A detailed document that lists all furniture items, materials, and finishes required for a project, including their quantities, specifications, and costs. In furniture and interior projects, the BoQ helps track:
- Individual furniture pieces and their variations (sizes, colors, finishes, fabrics)
- Unit prices and total costs
- Material specifications and quality standards

# WHAT THE PIPELINE LOOKS LIKE:
1. file upload basic processing using Gemini to extract product names & basic info like colors, designer, year & y-coordinates of product name to be used later
2. BoQ input. For each line of BoQ, we identify the product in our database and find its relevant price tables in the PDFs using y-coordinate ranges of our product & the next product
3. The relevant price table or tables are passed into a multimodal LLM, claude for accurate extraction of price based on attributes such as dimensions, color
4. combine all extracted data for the product in BoQ line & present to user. If user only provided a few attributes but not all of them that define the exact price, show the remaining attributes as filters for the user to choose froms
