# importer-api
Importer API to enable the execution of importer scripts outside the production server.

## Documentation

* ```/items/<item_id>/mapping```
Returns the Mardi ID and the Wikidata ID for a given item.
Wikidata IDs must be prefixed with ```wd:```

* ```/properties/<property_id>/mapping```
Returns the Mardi ID and the Wikidata ID for a given property.
Wikidata IDs must be prefixed with ```wdt:```

* ```/search/items/<label>```
Returns a list of item IDs that have the given label

* ```/search/properties/<label>```
Returns the property ID that has the given label
