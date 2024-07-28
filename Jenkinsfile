pipeline {
    agent {
        kubernetes {
            yamlFile 'build-pod.yaml'
            defaultContainer 'ez-docker-helm-build'
        }
    }
    environment {
        GITHUB_CREDENTIALS = credentials('git_hub')
        DOCKER_HUB_USERNAME = credentials('docker_hub')
        DOCKER_HUB_TOKEN = credentials('docker_hub')
        IMAGE_NAME = 'devote'
        TAG = 'latest'
        SLACK_CHANNEL = '#final-project'
        SLACK_CREDENTIAL_ID = 'slack-credentials'
        GITHUB_API_URL = 'https://api.github.com'
        GITHUB_REPO = 'glengol/DeVote'
        GIT_CREDENTIALS_ID = 'git_hub' // Ensure this matches your Jenkins credentials ID
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
            post {
                success {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Checkout' succeeded.")
                }
                failure {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Checkout' failed.")
                }
            }
        }
        stage('Set up Docker Buildx') {
            steps {
                script {
                    sh 'docker run --rm --privileged multiarch/qemu-user-static --reset -p yes'
                    sh 'docker buildx create --use'
                }
            }
            post {
                success {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Set up Docker Buildx' succeeded.")
                }
                failure {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Set up Docker Buildx' failed.")
                }
            }
        }
        stage('Login to DockerHub') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'docker_hub', passwordVariable: 'DOCKER_HUB_CREDENTIALS_PSW', usernameVariable: 'DOCKER_HUB_CREDENTIALS_USR')]) {
                        sh "echo \$DOCKER_HUB_CREDENTIALS_PSW | docker login -u \$DOCKER_HUB_CREDENTIALS_USR --password-stdin"
                    }
                }
            }
            post {
                success {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Login to DockerHub' succeeded.")
                }
                failure {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Login to DockerHub' failed.")
                }
            }
        }
        stage('Build and Run Containers') {
            steps {
                sh 'docker-compose up -d --build'
            }
            post {
                success {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Build and Run Containers' succeeded.")
                }
                failure {
                    slackSend(channel: "${SLACK_CHANNEL}", message: "Stage 'Build and Run Containers' failed.")
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
            steps {
                script {
                    sh 'docker build -t ${IMAGE_NAME}:${TAG} .'
                    sh 'docker tag ${IMAGE_NAME}:${TAG} glengold/${IMAGE_NAME}:${TAG}'
                    withCredentials([usernamePassword(credentialsId: 'docker_hub', passwordVariable: 'DOCKER_HUB_CREDENTIALS_PSW', usernameVariable: 'DOCKER_HUB_CREDENTIALS_USR')]) {
                        sh "docker login -u \$DOCKER_HUB_CREDENTIALS_USR -p \$DOCKER_HUB_CREDENTIALS_PSW"
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
        stage('Clean up') {
            steps {
                sh 'docker-compose down'
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

    post {
        success {
            slackSend(channel: "${SLACK_CHANNEL}", message: "Pipeline '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL}) succeeded.")
        }
        failure {
            slackSend(channel: "${SLACK_CHANNEL}", message: "Pipeline '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL}) failed.")
        }
    }
}
