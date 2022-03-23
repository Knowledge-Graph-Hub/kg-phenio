import uuid

from biolink_model_pydantic.model import ( #type: ignore
    PhenotypicFeature,
    Association,
    Predicate
)

from koza.cli_runner import koza_app #type: ignore

source_name="upheno_mapping_all"

row = koza_app.get_row(source_name)

# Entities

p1 = PhenotypicFeature(id=(((row["p1"]).split("/"))[-1]).replace("_",":"),
                            iri=row["p1"],
                            name=row["label_x"])
p2 = PhenotypicFeature(id=(((row["p2"]).split("/"))[-1]).replace("_",":"),
                            iri=row["p2"],
                            name=row["label_y"])

# Association
association = Association(
        id="uuid:" + str(uuid.uuid1()),
        subject=p1.id,
        predicate="Biolink:same_as",
        object=p2.id,
        relation="skos:exactMatch"
    )

koza_app.write(p1, association, p2)
