pipeline {
    agent {
        kubernetes {
            yamlFile 'build-pod.yaml'
            defaultContainer 'ez-docker-helm-build'
        }
    }
    environment {
        GIT_CREDENTIALS_ID = 'git_hub'
        DOCKER_CREDS = 'docker_hub'
        IMAGE_NAME = 'devote'
        SLACK_CHANNEL = '#final-project'
        SLACK_CREDENTIAL_ID = 'slack-credentials'
        GITHUB_API_URL = 'https://api.github.com' // For pull requests
        GITHUB_REPO = 'glengol/DeVote'
        HELM_REPO_CREDENTIALS_ID = 'helm_repo_github' // New credentials for the Helm repo
        BUILD_TAG = "1.0.${env.BUILD_NUMBER}"
        HELM_REPO_URL_PUSH = 'https://github.com/glengol/devote_helm.git'
    }
    stages {

        stage('Checkout Repositories') {
            steps {
                script {
                    // Checkout the main repository
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: '*/main']],
                        doGenerateSubmoduleConfigurations: false,
                        extensions: [],
                        userRemoteConfigs: [[
                            credentialsId: env.GIT_CREDENTIALS_ID,
                            url: 'https://github.com/glengol/DeVote.git'
                        ]]
                    ])
                    echo "Completed checkout of main repo"

                    // Checkout the Helm chart repository
                    dir('devote-helm-chart') {
                        checkout([
                            $class: 'GitSCM',
                            branches: [[name: 'main']],
                            doGenerateSubmoduleConfigurations: false,
                            extensions: [],
                            userRemoteConfigs: [[
                                credentialsId: env.HELM_REPO_CREDENTIALS_ID,
                                url: 'https://github.com/glengol/devote_helm.git'
                            ]]
                        ])
                        echo "Completed checkout of Helm chart repo"
                    }
                }
            }
            post {
                success {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Checkout Repositories' succeeded.")
                }
                failure {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Checkout Repositories' failed.")
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def buildTag = "1.0.${BUILD_NUMBER}"
                    def customImage = docker.build("glengold/${IMAGE_NAME}:${buildTag}")
                    env.CUSTOM_IMAGE = customImage.id
                    env.BUILD_TAG = buildTag
                }
            }
            post {
                success {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Build Docker Image' succeeded.")
                }
                failure {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Build Docker Image' failed.")
                }
            }
        }

        stage('Run Flask Application') {
            steps {
                script {
                    // Start the Flask application in the background
                    sh "docker run -d -p 5000:5000 --name flask_app ${CUSTOM_IMAGE} flask run --host=0.0.0.0"

                    // Give the Flask application a moment to start
                    sleep 10
                }
            }
            post {
                success {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Run Flask Application' succeeded.")
                }
                failure {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Run Flask Application' failed.")
                }
            }
        }

        stage('Install Dependencies and Run Tests') {
            steps {
                container('python-test') {
                    script {
                        sh 'pytest'
                    }
                }
            }
            post {
                success {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Install Dependencies and Run Tests' succeeded.")
                }
                failure {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Install Dependencies and Run Tests' failed.")
                }
            }
        }

        stage('Push Image to Docker Hub') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // Check if the image exists locally
                    def imageExists = sh(script: "docker images -q ${CUSTOM_IMAGE}", returnStdout: true).trim()
                    if (imageExists) {
                        withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDS, passwordVariable: 'DOCKER_HUB_CREDENTIALS_PSW', usernameVariable: 'DOCKER_HUB_CREDENTIALS_USR')]) {
                            sh "echo \$DOCKER_HUB_CREDENTIALS_PSW | docker login -u \$DOCKER_HUB_CREDENTIALS_USR --password-stdin"
                        }
                        sh "docker push glengold/${IMAGE_NAME}:${BUILD_TAG}"
                    } else {
                        error "Docker image ${CUSTOM_IMAGE} does not exist locally."
                    }
                }
            }
            post {
                success {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Push Image to Docker Hub' succeeded.")
                }
                failure {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Push Image to Docker Hub' failed.")
                }
            }
        }

        stage('Update Helm Chart and Push') {
            when {
                branch 'main'
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: env.GIT_CREDENTIALS_ID, usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                        dir('devote-helm-chart') {
                            sh '''
                                ls -la
                                git config --global --add safe.directory /home/jenkins/agent/workspace/devote-ci_main/devote-helm-chart
                                git config --global user.email "jenkins@example.com"
                                git config --global user.name "Jenkins CI"
                                
                                # Ensure we are on the correct branch
                                git checkout main
                                git pull origin main

                                # Update chart files
                                sed -i "s/^version:.*/version: ${BUILD_TAG}/" devote-helm-chart/Chart.yaml
                                cat devote-helm-chart/Chart.yaml
                                sed -i "s/^  tag:.*/  tag: ${BUILD_TAG}/" devote-helm-chart/values.yaml
                                cat devote-helm-chart/values.yaml

                                # Package Helm chart
                                helm package ./devote-helm-chart
                                helm repo index --url https://glengol.github.io/devote_helm ./devote-helm-chart

                                # Add, commit, and push changes
                                git add .
                                git commit -m "Update Helm chart version to ${BUILD_TAG} and image tag to ${BUILD_TAG}"
                                git push https://${USERNAME}:${PASSWORD}@github.com/glengol/devote_helm.git main
                            '''
                        }
                    }
                }
            }    
            post {
                success {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Update Helm Chart and Push' succeeded.")
                }
                failure {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Update Helm Chart and Push' failed.")
                }
            }
        }

        stage('Create Merge Request') {
            when {
                not {
                    branch 'main'
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: env.GIT_CREDENTIALS_ID, usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                    script {
                        def branchName = env.BRANCH_NAME
                        def pullRequestTitle = "Merge ${branchName} into main"
                        def pullRequestBody = "Automatically generated merge request for branch ${branchName} from Jenkins"

                        sh """
                            curl -X POST -u ${USERNAME}:${PASSWORD} \
                            -d '{ "title": "${pullRequestTitle}", "body": "${pullRequestBody}", "head": "${branchName}", "base": "main" }' \
                            ${GITHUB_API_URL}/repos/${GITHUB_REPO}/pulls
                        """
                    }
                }
            }
        }

        stage('Clean up') {
            steps {
                script {
                    // Stop and remove the Flask container
                    sh 'docker stop flask_app && docker rm flask_app'
                }
            }
            post {
                success {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Clean up' succeeded.")
                }
                failure {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Clean up' failed.")
                }
            }
        }
    }
    post {
        success {
            slackSend(channel: "${SLACK_CHANNEL}", message: "Pipeline '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL}) succeeded.")
        }
        failure {
            slackSend(channel: "${SLACK_CHANNEL}", message: "Pipeline '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL}) failed.")
        }
    }
}
