#!groovy

properties (
    [                                                                           
		 buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '', daysToKeepStr: '', numToKeepStr: '10')),
         [$class: 'CopyArtifactPermissionProperty', projectNames: '*'],
         pipelineTriggers([[$class: 'PeriodicFolderTrigger', interval: '1d']])  
	]  
)

def prepareEnv() {
	deleteDir()
	unstash "binaries"
	
	env.WORKSPACE = pwd()

	sh "find ${env.WORKSPACE}"

	sh "mkdir -p SPECS SOURCES"
	sh "cp build/distributions/*.zip SOURCES/upsilon-custodian.zip"
}

def buildDockerContainer() {
	prepareEnv()

	unstash 'el7'
	sh 'mv RPMS/noarch/*.rpm RPMS/noarch/upsilon-custodian.rpm'

	sh 'unzip -jo SOURCES/upsilon-custodian.zip "upsilon-custodian-*/var/pkg/Dockerfile" "upsilon-custodian-*/.buildid" -d . '

	tag = sh script: 'buildid -pk tag', returnStdout: true

	println "tag: ${tag}"

	sh "docker build -t 'upsilonproject/custodian:${tag}' ."
	sh "docker tag 'upsilonproject/custodian:${tag}' 'upsilonproject/custodian:latest' "
	sh "docker save upsilonproject/custodian:${tag} | gzip > upsilon-custodian-docker-${tag}.tgz"

	archive "upsilon-custodian-docker-${tag}.tgz"
}
 



def buildRpm(dist) {                                                               
    prepareEnv()                                                                   
                                                                                    
    sh 'unzip -jo SOURCES/upsilon-custodian.zip "upsilon-custodian-*/var/pkg/upsilon-custodian.spec" "upsilon-custodian-*/.buildid.rpmmacro" -d SPECS/'
    sh "find ${env.WORKSPACE}"                                                     
                                                                                   
    sh "rpmbuild -ba SPECS/upsilon-custodian.spec --define '_topdir ${env.WORKSPACE}' --define 'dist ${dist}'"
                                                                                   
    archive 'RPMS/noarch/*.rpm'                                                    
	stash "${dist}"
}                                                                                  

node {
	stage("Build") {
		deleteDir()

		checkout scm
		sh './make.sh'	

		archive 'build/distributions/**'

		stash includes: 'build/distributions/**', name: 'binaries'
	}

	stage("Package") {
		buildRpm("el7")
		buildRpm("el6")
		buildDockerContainer()
	}
}
