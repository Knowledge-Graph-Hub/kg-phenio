CONFIGDIR=config
SOURCESDIR=sources
PROJECTSDIR=projects
KGXCONFIGDIR=kgx-config

DATADIR=data
DATA_RAWDIR=$(DATADIR)/raw
DATA_BASEPLUS=$(DATADIR)/baseplus
MATCHESDIR=$(DATADIR)/matches
KGXDIR=$(DATADIR)/kgx
NEATDIR=$(DATADIR)/neat

MONARCH_OWL="monarch.owl"

ROBOT=robot -v

$(KGXDIR)/%/ $(NEATDIR)/%/ $(MATCHESDIR)/%/:
	mkdir -p $@

####################################
###### Sources #####################
####################################

all: prepare_sources

.PHONY: prepare_sources

# We want to repeat this for every OWL version, not just the original, but for now we just use the main OWL
prepare_sources:
	
	export ROBOT_JAVA_ARGS=-Xmx20G

	mkdir -p $(DATA_RAWDIR)/ $(DATADIR)/

	./scripts/prepare_monarch_subsets.sh
	mv *.owl $(DATA_RAWDIR)

## This is the memory-intensive step
	$(ROBOT) merge --input $(DATA_RAWDIR)/monarch.owl reason --reasoner ELK --output $(DATA_BASEPLUS)/monarch-baseplus.owl

#######################################
#### KGX files ########################
#######################################

all: prepare_kgx

.PHONY: prepare_kgx

# We want to repeat this for every OWL version, not just the original
prepare_kgx: 
	mkdir -p $(KGXDIR)
	kgx transform --input $(DATA_RAWDIR)/monarch.owl --input-format owl --output-format tsv --output $(KGXDIR)/monarch/monarch-tsv

###################################
#### Prepare embedding pipelines ##
###################################

#all: embedding

#.PHONY: embedding

# Upload to S3 with dated build