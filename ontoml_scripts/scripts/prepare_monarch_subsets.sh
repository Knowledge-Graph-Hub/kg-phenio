#!/bin/sh
# Script for retrieving and preparing subsets of monarch.owl.
# This starts with the pre-merged monarch.owl version as 
# performing a merge on all versions is very memory-intensive.
# Instead, it uses 'robot remove' to remove all entities from
# a given namespace's axioms.
# Note that the merged monarch.owl is >900MB so the total 
# disk size of outputs will be substantial.

MONARCH_OWL_URL="https://data-test.monarchinitiative.org/monarch/202109/owl/monarch-merged.owl"
MONARCH_OWL="monarch-merged.owl"

# These are the ontologies to ablate
# we need to name the specific .owl to remove
# but leave off the suffix so we can create the filenames
remove_prefixes="MONDO"

if [ -f "$MONARCH_OWL" ]; then
    echo "Found $MONARCH_OWL"
else
    echo "Retrieving monarch-merged.owl"
    wget $MONARCH_OWL_URL
fi

echo "Preparing import ablations of $MONARCH_OWL"

export ROBOT_JAVA_ARGS=-Xmx16G
for prefix in $remove_prefixes; do
    echo $prefix
    outname = "monarch-merged-no_${prefix}.owl"
    echo "Preparing $outname ..."
    robot remove --input $MONARCH_OWL --select "<http://purl.obolibrary.org/obo/$prefix_*>" --signature true --output $outname
    #robot remove --input $MONARCH_OWL --select "<http://purl.obolibrary.org/obo/MONDO_*>" --signature true --output monarch-merged-no_MONDO.owl
done

echo "Complete."



