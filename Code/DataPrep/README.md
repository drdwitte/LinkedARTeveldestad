#Data Preparation

Scripts to build an ETL pipeline

# Download collection objects (author: Jelle VH)
`python .\coghent\download_graphql.py [output_object_directory] --limit [limit] --skip [skip] --relation [relation]`

|Museum| Relation|
|-|-|
| Industriemuseum | entities/07670944-3244-4132-8b3d-0a57cf67c8d6 |
| Design Museum Gent | entities/116a59ef-fb84-412f-9631-4653eb0e5264 |
| STAM - Stadsmuseum Gent | entities/f65f1cf0-5fc3-4dd4-a190-60b4166ce8df |
| Huis van Alijn | entities/94c0a4e6-0511-473b-939a-93c5fa989d9a |
| Archief Gent | entities/358c1bdc-bcd7-45ab-8b93-e2cd85d21aca |

# Download object images (author: Jelle VH)
`python .\coghent\download_images.py [input_object_directory] [output_image_directory]`


#RouteYou Client requires a key!