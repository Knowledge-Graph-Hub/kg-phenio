pipeline {
    agent {
        docker {
            reuseNode false
            image 'caufieldjh/kg-hub-3_10:4'
        }
    }
    triggers{
        cron('0 9 8 1-12 *')
    }
    environment {
        BUILDSTARTDATE = sh(script: "echo `date +%Y%m%d`", returnStdout: true).trim()
        S3PROJECTDIR = 'kg-phenio' // no trailing slash

        // Distribution ID for the AWS CloudFront for this bucket
        // used solely for invalidations
        AWS_CLOUDFRONT_DISTRIBUTION_ID = 'EUVSWXZQBXCFP'

        MERGEDKGNAME_BASE = "kg-phenio"
        MERGEDKGNAME_GENERIC = "merged-kg"
    }
    options {
        timestamps()
        disableConcurrentBuilds()
    }
    stages {
        // Very first: pause for a minute to give a chance to
        // cancel and clean the workspace before use.
        stage('Ready and clean') {
            steps {
                // Give us a minute to cancel if we want.
                sleep time: 30, unit: 'SECONDS'
            }
        }

        stage('Initialize') {
            steps {
                // print some info
                dir('./gitrepo') {
                    sh 'env > env.txt'
                    sh 'echo $BRANCH_NAME > branch.txt'
                    sh 'echo "$BRANCH_NAME"'
                    sh 'cat env.txt'
                    sh 'cat branch.txt'
                    sh "echo $BUILDSTARTDATE > dow.txt"
                    sh "echo $BUILDSTARTDATE"
                    sh "echo $MERGEDKGNAME_BASE"
                    sh "echo $MERGEDKGNAME_GENERIC"
                    sh "python3.10 --version"
                    sh "id"
                    sh "whoami" // this should be jenkinsuser
                    // if the above fails, then the docker host didn't start the docker
                    // container as a user that this image knows about. This will
                    // likely cause lots of problems (like trying to write to $HOME
                    // directory that doesn't exist, etc), so we should fail here and
                    // have the user fix this

                }
            }
        }

        stage('Build kg_phenio') {
            steps {
                dir('./gitrepo') {
                    git(
                            url: 'https://github.com/Knowledge-Graph-Hub/kg-phenio',
                            branch: env.BRANCH_NAME
                    )
                    sh '/usr/bin/python3.10 -m venv venv'
                    sh '. venv/bin/activate'
                    sh './venv/bin/pip install .'
                    sh './venv/bin/pip install awscli boto3 s3cmd'
                }
            }
        }

        stage('Download') {
            steps {
                dir('./gitrepo') {
                    script {
                        
                        // Verify that the project directory is defined, or it will make a mess
                        // when it uploads everything to the wrong directory
                        if (S3PROJECTDIR.replaceAll("\\s","") == '') {
                            error("Project name contains only whitespace. Will not continue.")
                        }

                        def run_py_dl = sh(
                            script: '. venv/bin/activate && python3.10 run.py download', returnStatus: true
                        )
                        if (run_py_dl == 0) {
                            if (env.BRANCH_NAME != 'master') { // upload raw to s3 if we're on correct branch
                                echo "Will not push if not on correct branch."
                            } else {
                                withCredentials([file(credentialsId: 's3cmd_kg_hub_push_configuration', variable: 'S3CMD_CFG')]) {
                                    sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG --acl-public --mime-type=plain/text --cf-invalidate put -r data/raw s3://kg-hub-public-data/$S3PROJECTDIR/'
                                }
                            }
                        }  else { // 'run.py download' failed - let's try to download last good copy of raw/ from s3 to data/
                            currentBuild.result = "UNSTABLE"
                            withCredentials([file(credentialsId: 's3cmd_kg_hub_push_configuration', variable: 'S3CMD_CFG')]) {
                                sh 'rm -fr data/raw || true;'
                                sh 'mkdir -p data/raw || true'
                                sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG --acl-public --mime-type=plain/text get -r s3://kg-hub-public-data/$S3PROJECTDIR/raw/ data/raw/'
                            }
                        }
                    }
                }
            }
        }

        stage('Transform') {
            steps {
                dir('./gitrepo') {
		            sh '. venv/bin/activate && env && python3.10 run.py transform'
                }
            }
        }

        stage('Merge') {
            steps {
                dir('./gitrepo') {
                    sh '. venv/bin/activate && python3.10 run.py merge -y merge.yaml'
		            sh 'cp merged_graph_stats.yaml merged_graph_stats_$BUILDSTARTDATE.yaml'
                    sh 'mv data/merged/merged-kg_nodes.tsv .'
                    sh 'mv data/merged/merged-kg_edges.tsv .'
                    sh 'tar -czvf merged-kg.tar.gz merged-kg_nodes.tsv merged-kg_edges.tsv merged_graph_stats_$BUILDSTARTDATE.yaml'
                }
            }
        }

        stage('Publish') {
            steps {
                dir('./gitrepo') {
                    script {

                        // make sure we aren't going to clobber existing data
                        withCredentials([file(credentialsId: 's3cmd_kg_hub_push_configuration', variable: 'S3CMD_CFG')]) {
                            REMOTE_BUILD_DIR_CONTENTS = sh (
                                script: '. venv/bin/activate && s3cmd -c $S3CMD_CFG ls s3://kg-hub-public-data/$S3PROJECTDIR/$BUILDSTARTDATE/',
                                returnStdout: true
                            ).trim()
                            echo "REMOTE_BUILD_DIR_CONTENTS (THIS SHOULD BE EMPTY): '${REMOTE_BUILD_DIR_CONTENTS}'"
                            if("${REMOTE_BUILD_DIR_CONTENTS}" != ''){
                                echo "Will not overwrite existing remote S3 directory: $S3PROJECTDIR/$BUILDSTARTDATE"
                                sh 'exit 1'
                            } else {
                                echo "remote directory $S3PROJECTDIR/$BUILDSTARTDATE is empty, proceeding"
                            }
                        }

                        if (env.BRANCH_NAME != 'master') {
                            echo "Will not push if not on correct branch."
                        } else {
                            withCredentials([
					            file(credentialsId: 's3cmd_kg_hub_push_configuration', variable: 'S3CMD_CFG'),
					            file(credentialsId: 'aws_kg_hub_push_json', variable: 'AWS_JSON'),
					            string(credentialsId: 'aws_kg_hub_access_key', variable: 'AWS_ACCESS_KEY_ID'),
					            string(credentialsId: 'aws_kg_hub_secret_key', variable: 'AWS_SECRET_ACCESS_KEY')]) {
                                                              
                                //
                                // make $BUILDSTARTDATE/ directory and sync to s3 bucket
                                //
                                sh 'mkdir $BUILDSTARTDATE/'
                                // sh 'cp -p data/merged/${MERGEDKGNAME_BASE}.nt.gz $BUILDSTARTDATE/${MERGEDKGNAME_BASE}.nt.gz'
                                sh 'cp -p merged-kg.tar.gz $BUILDSTARTDATE/${MERGEDKGNAME_BASE}.tar.gz'

                                // transformed data
                                sh 'rm -fr data/transformed/.gitkeep'
                                sh 'cp -pr data/transformed $BUILDSTARTDATE/'
                                sh 'cp -pr data/raw $BUILDSTARTDATE/'
                                sh 'cp Jenkinsfile $BUILDSTARTDATE/'

                                // copy that NEAT config, too
                                // but update its buildname internally first
                                sh """ sed -i '/      - path:/ s/BUILDNAME/$BUILDSTARTDATE/' neat.yaml """
                                sh """ sed -i '/  s3_bucket_dir:/ s/kg-phenio/$S3PROJECTDIR\\/$BUILDSTARTDATE\\/graph_ml/' neat.yaml """
                                sh 'cp neat.yaml $BUILDSTARTDATE/'

                                // stats dir
                                sh 'mkdir $BUILDSTARTDATE/stats/'
                                sh 'cp -p *_stats.yaml $BUILDSTARTDATE/stats/'
				
                                // build the index, then upload to remote
                                sh '. venv/bin/activate && multi_indexer -v --directory $BUILDSTARTDATE --prefix https://kg-hub.berkeleybop.io/$S3PROJECTDIR/$BUILDSTARTDATE -x -u'

                                sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG put -pr --acl-public --cf-invalidate $BUILDSTARTDATE s3://kg-hub-public-data/$S3PROJECTDIR/'
                                sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG rm -r s3://kg-hub-public-data/$S3PROJECTDIR/current/'
                                sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG put -pr --acl-public --cf-invalidate $BUILDSTARTDATE/* s3://kg-hub-public-data/$S3PROJECTDIR/current/'

                                // make index for project dir
                                sh '. venv/bin/activate && multi_indexer -v --prefix https://kg-hub.berkeleybop.io/$S3PROJECTDIR/ -b kg-hub-public-data -r $S3PROJECTDIR -x'
                                sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG put -pr --acl-public --cf-invalidate ./index.html s3://kg-hub-public-data/$S3PROJECTDIR/'

                                // Invalidate the CDN now that the new files are up.
                                sh 'echo "[preview]" > ./awscli_config.txt && echo "cloudfront=true" >> ./awscli_config.txt'
                                sh '. venv/bin/activate && AWS_CONFIG_FILE=./awscli_config.txt python3.10 ./venv/bin/aws cloudfront create-invalidation --distribution-id $AWS_CLOUDFRONT_DISTRIBUTION_ID --paths "/*"'

                                // Should now appear at:
                                // https://kg-hub.berkeleybop.io/kg-phenio/
                            }

                        }
                    }
                }
            }
        }

    }

    post {
        always {
            echo 'In always'
            echo 'Cleaning workspace...'
            cleanWs()
        }
        success {
            echo 'I succeeded!'
        }
        unstable {
            echo 'I am unstable :/'
        }
        failure {
            echo 'I failed :('
        }
        changed {
            echo 'Things were different before...'
        }
    }
}
