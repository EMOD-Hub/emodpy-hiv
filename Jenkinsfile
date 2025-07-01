podTemplate(
    //idleMinutes : 30,
    podRetention : onFailure(),
    activeDeadlineSeconds : 3600,
    containers: [
        containerTemplate(
            name: 'dtk-rpm-builder', 
            image: 'docker-production.packages.idmod.org/idm/dtk-rpm-builder:0.1',
            command: 'sleep', 
            args: '30d'
            )
  ]) {
  node(POD_LABEL) {
    container('dtk-rpm-builder'){
			def build_ok = true
			stage('Cleanup Workspace') {		    
				cleanWs()
				echo "Cleaned Up Workspace For Project"
				echo "${params.BRANCH}"
			}
			stage('Prepare') {
				sh 'python3 --version'
				sh 'pip3 --version'

				sh 'python3 -m pip install --upgrade pip'
				sh "pip3 install wheel "
				sh "pip3 install build"
				sh 'python3 -m pip install --upgrade setuptools'
				sh 'pip3 freeze'
			}
		stage('Code Checkout') {
			if (env.CHANGE_ID) {
				echo "I execute on the pull request ${env.CHANGE_ID}"
				checkout([$class: 'GitSCM',
				branches: [[name: "pr/${env.CHANGE_ID}/head"]],
				doGenerateSubmoduleConfigurations: false,
				extensions: [],
				gitTool: 'Default',
				submoduleCfg: [],
				userRemoteConfigs: [[refspec: '+refs/pull/*:refs/remotes/origin/pr/*', credentialsId: '704061ca-54ca-4aec-b5ce-ddc7e9eab0f2', url: 'git@github.com:InstituteforDiseaseModeling/emodpy-hiv.git']]])
			} else {
				echo "Running on ${env.BRANCH_NAME} branch"
				git branch: "${env.BRANCH_NAME}",
				credentialsId: '704061ca-54ca-4aec-b5ce-ddc7e9eab0f2',
				url: 'git@github.com:InstituteforDiseaseModeling/emodpy-hiv.git'
			}
		}
		stage('Build') {
			sh 'pwd'
			sh 'ls -a'
			sh 'python3 -m build wheel'
			 
		}
		stage('Install') {
			def curDate = sh(returnStdout: true, script: "date").trim()
			echo "The current date is ${curDate}"
			
			echo "Installing emodpy-hiv from wheel file built from code."
			def wheelFile = sh(returnStdout: true, script: "find ./dist -name '*.whl'").toString().trim()
			echo "Package file: ${wheelFile}"
			sh "pip3 install $wheelFile --extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple"
			sh "pip3 install dataclasses"
			sh 'pip3 install keyrings.alt'
			sh "pip3 freeze"
		}
		stage('Login') {withCredentials([string(credentialsId: 'Comps_emodpy_user', variable: 'user'), string(credentialsId: 'Comps_emodpy_password', variable: 'password')])
				{
				sh 'curl --user $user:$password https://comps2.idmod.org'
				}
			}
			
		try{
			stage('Unit Test') {
				echo "Running Unit test Tests"
				dir('tests/unittests') {
					sh "pip3 install unittest-xml-reporting"
					sh 'python3 -m xmlrunner discover'
					junit allowEmptyResults: true, testResults: '*.xml'
				}
			}
		} catch(e) {
			build_ok = false
			echo e.toString()  
		}
		stage('Login')
		{
			withCredentials([usernamePassword(credentialsId: 'comps_jenkins_user', usernameVariable: 'COMPS_USERNAME', passwordVariable: 'COMPS_PASSWORD'),
			                 usernamePassword(credentialsId: 'comps2_jenkins_user', usernameVariable: 'COMPS2_USERNAME', passwordVariable: 'COMPS2_PASSWORD')]) {
				dir('tests') {
				    sh "pip3 install 'urllib3<2.0' --force-reinstall"
				    sh 'python3 create_auth_token_args.py --comps_url https://comps2.idmod.org --username $COMPS2_USERNAME --password $COMPS2_PASSWORD'
				    sh 'python3 create_auth_token_args.py --comps_url https://comps.idmod.org --username $COMPS_USERNAME --password $COMPS_PASSWORD'
				    
				}
			}
		}
		try{
			stage('Workflow Tests') {
				echo "Running Workflow Tests"
				dir('tests/sim_tests') {
				 	sh 'python3 -m xmlrunner discover'
				 	junit allowEmptyResults: true, testResults: '*.xml'
				}
			}
		} catch(e) {
			build_ok = false
			echo e.toString()  
		}
		
		stage('Run Examples') {		    
		 	echo "Running examples"
		 		dir('examples') {
		 			sh 'pip3 install snakemake'
					sh 'pip3 install pulp==2.7.0'
		 			sh 'snakemake --cores=10 --config python_version=python3'
		 		}
		 	}
		if(build_ok) {
			currentBuild.result = "SUCCESS"
		} else {
			currentBuild.result = "FAILURE"
		}
	   }
      }
}
