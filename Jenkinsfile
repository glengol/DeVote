pipeline {
    agent any

    environment {
        SLACK_WEBHOOK_URL = credentials('SLACK_WEBHOOK_URL')
        GITHUB_CREDENTIALS = credentials('git_hub')
        DOCKER_HUB_USERNAME = credentials('docker_hub')
        DOCKER_HUB_TOKEN = credentials('docker_hub')
        IMAGE_NAME = 'devote'
        TAG = 'latest'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set up Docker Buildx') {
            steps {
                script {
                    sh 'docker run --rm --privileged multiarch/qemu-user-static --reset -p yes'
                    sh 'docker buildx create --use'
                }
            }
        }

        stage('Login to DockerHub') {
            steps {
                script {
                    sh "echo ${DOCKER_HUB_TOKEN} | docker login -u ${DOCKER_HUB_USERNAME} --password-stdin"
                }
            }
        }

        stage('Set up Docker Compose') {
            steps {
                sh 'sudo apt-get update && sudo apt-get install -y docker-compose'
            }
        }

        stage('Build and Run Containers') {
            steps {
                sh 'docker-compose up -d --build'
            }
        }

        stage('Run Pytest') {
            steps {
                sh 'pytest'
            }
        }

        stage('Bump Version and Push Tag') {
            when {
                branch 'main'
            }
            steps {
                script {
                    def gitTag = sh(script: 'git describe --tags', returnStdout: true).trim()
                    env.TAG = gitTag

                    sh 'docker build -t ${IMAGE_NAME}:${TAG} .'
                    sh 'docker tag ${IMAGE_NAME}:${TAG} glengold/${IMAGE_NAME}:${TAG}'
                    sh 'docker push glengold/${IMAGE_NAME}:${TAG}'
                }
            }
        }

        stage('Clean up') {
            steps {
                sh 'docker-compose down'
            }
        }
    }

    post {
        success {
            slackSend (
                channel: '#your-slack-channel',
                color: 'good',
                message: "✅ CI Pipeline succeeded for commit ${env.GIT_COMMIT}.\nPytest tests passed and Docker image ${env.IMAGE_NAME}:${env.TAG} has been pushed successfully.",
                webhookURL: "${SLACK_WEBHOOK_URL}"
            )
        }

        failure {
            slackSend (
                channel: '#your-slack-channel',
                color: 'danger',
                message: "❌ CI Pipeline failed for commit ${env.GIT_COMMIT}.",
                webhookURL: "${SLACK_WEBHOOK_URL}"
            )
        }
    }
}
