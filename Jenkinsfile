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
        TAG = 'latest'
        SLACK_CHANNEL = '#final-project'
        SLACK_CREDENTIAL_ID = 'slack-credentials'
        GITHUB_API_URL = 'https://api.github.com' // For pull requests
        GITHUB_REPO = 'glengol/DeVote'
    }
    stages {

        stage('Checkout SCM') {
            steps {
                script {
                    // Checkout the main repository
                    checkout scm
                    echo "Completed checkout of main repo"
                }
            }
            post {
                success {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Checkout SCM' succeeded.")
                }
                failure {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Checkout SCM' failed.")
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def buildTag = "${IMAGE_NAME}:${TAG}.${BUILD_NUMBER}"
                    def customImage = docker.build(buildTag)
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
                    sh 'docker run -d -p 5000:5000 --name flask_app glengold/${IMAGE_NAME}:${TAG} flask run --host=0.0.0.0'

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
                    withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDS, passwordVariable: 'DOCKER_HUB_CREDENTIALS_PSW', usernameVariable: 'DOCKER_HUB_CREDENTIALS_USR')]) {
                        sh "echo \$DOCKER_HUB_CREDENTIALS_PSW | docker login -u \$DOCKER_HUB_CREDENTIALS_USR --password-stdin"
                    }
                    sh 'docker push glengold/${IMAGE_NAME}:${TAG}'
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

        stage('Create merge request') {
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
                            curl -X POST -u ${PASSWORD}:x-oauth-basic \
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
