#!groovy

properties (
     [                                                                           
         [                                                                       
             $class: 'jenkins.model.BuildDiscarderProperty', strategy: [$class: 'LogRotator', numToKeepStr: '10', artifactNumToKeepStr: '10'],
             $class: 'CopyArtifactPermissionProperty', projectNames: '*'         
         ]                                                                       
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

	sh "docker build -t 'upsilonproject/drone:${tag}' ."
	sh "docker save upsilonproject/drone:${tag} > upsilon-drone-docker-${tag}.tgz"

	archive "upsilon-drone-docker-${tag}.tgz"
}
 



def buildRpm(dist) {                                                               
    prepareEnv()                                                                   
                                                                                    
    sh 'unzip -jo SOURCES/upsilon-custodian.zip "upsilon-custodian-*/var/pkg/upsilon-custodian.spec" "upsilon-custodian-*/.buildid.rpmmacro" -d SPECS/'
    sh "find ${env.WORKSPACE}"                                                     
                                                                                   
    sh "rpmbuild -ba SPECS/upsilon-custodian.spec --define '_topdir ${env.WORKSPACE}' --define 'dist ${dist}'"
                                                                                   
    archive 'RPMS/noarch/*.rpm'                                                    
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
